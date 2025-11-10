# warehouse/telegram_utils.py
import io
import json
import time
import threading
from pathlib import Path
from typing import Optional

import requests
from PIL import Image
from django.utils.html import escape
from django.urls import reverse
from django.conf import settings

from user_profile.models import Profile

# --- Ваши токены ---
TELEGRAM_BOT_TOKEN = '7614699995:AAFIFb7LFtZPO3wBJnNQozKROJ6A-SKEql4'
CHAT_ID = '-1002649895374'
# --------------------

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# где храним соответствие { part_id: telegram_message_id } (чтобы потом удалить пост)
MAP_FILE = Path(getattr(settings, "BASE_DIR", Path(__file__).resolve().parents[2])) / "telegram_message_map.json"
_MAP_LOCK = threading.Lock()

# простая защита от дублей (на короткое время)
_SENT_CACHE: dict[int, float] = {}
_SENT_TTL_SEC = 120

# настройки обработки вертикальных фото
SQUARE_SIDE = 800
JPEG_QUALITY = 85


# ----------------- утилиты антидубликатов / map -----------------
def _recently_sent(part_id: int) -> bool:
    now = time.time()
    stale = [pid for pid, ts in _SENT_CACHE.items() if now - ts > _SENT_TTL_SEC]
    for pid in stale:
        _SENT_CACHE.pop(pid, None)
    return part_id in _SENT_CACHE

def _mark_sent(part_id: int) -> None:
    _SENT_CACHE[part_id] = time.time()

def _load_map() -> dict:
    with _MAP_LOCK:
        if MAP_FILE.exists():
            try:
                return json.loads(MAP_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

def _save_map(data: dict) -> None:
    with _MAP_LOCK:
        try:
            MAP_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[telegram] map save error: {e}")

def _set_message_id(part_id: int, message_id: int) -> None:
    data = _load_map()
    data[str(part_id)] = message_id
    _save_map(data)

def _pop_message_id(part_id: int) -> Optional[int]:
    data = _load_map()
    mid = data.pop(str(part_id), None)
    _save_map(data)
    return mid


# ----------------- текст -----------------
def _device_with_ending(device: Optional[str]) -> str:
    if not device:
        return ""
    d = device.lower()
    if d in ("телефон", "планшет"):
        return d + "а"
    if d == "смарт-часы":
        return "смарт-часов"
    return device

def _seller_username(part) -> str:
    try:
        profile = Profile.objects.get(user=part.user)
        tg = (profile.telegram_username or "").strip()
        if tg:
            return "@" + tg.lstrip("@")
    except Profile.DoesNotExist:
        pass
    return part.user.username

def _build_part_url(part, request=None) -> str:
    url = reverse("part_detail", args=[part.id])
    if request is not None:
        try:
            return request.build_absolute_uri(url)
        except Exception:
            return url
    return url

def _build_caption(part, request=None) -> str:
    device_end = escape(_device_with_ending(part.device))
    part_type = escape(part.part_type or "")
    brand = escape(part.brand or "")
    model = escape(getattr(part, "display_model", None) or part.model or "")
    price = escape(str(part.price))
    seller = escape(_seller_username(part))
    city = escape(getattr(getattr(part.user, "profile", None), "city", "") or "")

    part_url = _build_part_url(part, request=request)
    link_html = f'<a href="{part_url}">Открыть объявление</a>'

    caption = (
        f"🧩 <b>{part_type}</b>\n"
        f"• для {device_end}, <b>{brand} {model}</b>\n"
        f"• Цена: <b>{price} руб</b>\n"
        f"• Продавец: {seller}"
        + (f"\n• Город: {city}" if city else "")
        + f"\n{link_html}"
    ).strip()
    return caption


# ----------------- фото -----------------
def _first_image_url(part, request=None) -> Optional[str]:
    img_obj = part.images.first()
    if not img_obj or not getattr(img_obj, "image", None):
        return None
    url = getattr(img_obj.image, "url", None)
    if not url:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if request is not None:
        try:
            return request.build_absolute_uri(url)
        except Exception:
            return url
    return url

def _fetch_image(url: str) -> Optional[bytes]:
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.content
    except requests.RequestException as e:
        print(f"[telegram] fetch image error: {e}")
        return None

def _square_crop_if_vertical(image_bytes: bytes) -> Optional[bytes]:
    """
    Если фото вертикальное (H/W > 1.05) — делаем центр-кроп до квадрата и
    уменьшаем до SQUARE_SIDE. Горизонтальные/квадратные — возвращаем None
    (это сигнал отправлять исходник по URL без обработки).
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as im:
            im = im.convert("RGB")
            w, h = im.size
            if h / max(1, w) <= 1.05:
                # горизонтальное или почти квадрат — НЕ трогаем
                return None

            # центр-кроп до квадрата по меньшей стороне (w)
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            im = im.crop((left, top, left + side, top + side))

            # ресайз до SQUARE_SIDE
            im = im.resize((SQUARE_SIDE, SQUARE_SIDE), Image.LANCZOS)

            out = io.BytesIO()
            im.save(
                out,
                format="JPEG",
                quality=JPEG_QUALITY,
                optimize=True,
                progressive=True,
                subsampling="4:2:0",
            )
            return out.getvalue()
    except Exception as e:
        print(f"[telegram] crop error: {e}")
        return None


# ----------------- отправка / удаление -----------------
def _send_message(text: str) -> Optional[int]:
    try:
        r = requests.post(
            f"{API_BASE}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("result", {}).get("message_id")
    except requests.RequestException as e:
        print(f"[telegram] sendMessage error: {e}")
        return None

def _send_photo_with_bytes(photo_bytes: bytes, caption: str) -> Optional[int]:
    files = {"photo": ("part.jpg", photo_bytes, "image/jpeg")}
    data = {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"}
    try:
        r = requests.post(f"{API_BASE}/sendPhoto", data=data, files=files, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("result", {}).get("message_id")
    except requests.RequestException as e:
        print(f"[telegram] sendPhoto(bytes) error: {e}")
        return None

def _send_photo_by_url(photo_url: str, caption: str) -> Optional[int]:
    try:
        r = requests.post(
            f"{API_BASE}/sendPhoto",
            data={"chat_id": CHAT_ID, "photo": photo_url, "caption": caption, "parse_mode": "HTML"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("result", {}).get("message_id")
    except requests.RequestException as e:
        print(f"[telegram] sendPhoto(url) error: {e}")
        return None

def delete_telegram_message_for_part(part_id: int) -> bool:
    mid = _pop_message_id(part_id)
    if not mid:
        return False
    try:
        r = requests.post(
            f"{API_BASE}/deleteMessage",
            data={"chat_id": CHAT_ID, "message_id": mid},
            timeout=15,
        )
        return r.status_code == 200
    except requests.RequestException as e:
        print(f"[telegram] deleteMessage error: {e}")
        return False


# ----------------- публичная -----------------
def send_new_part_notification(part, request=None) -> bool:
    """
    Отправляем одно сообщение о запчасти.
    • Горизонтальные/квадратные фото: без изменений — отправка по URL.
    • Вертикальные фото: центр-кроп до квадрата 800×800.
    • Подпись: HTML + ссылка внутри сообщения.
    • Сохраняем message_id для последующего удаления.
    • Простая защита от дублей.
    """
    if not getattr(part, "id", None):
        return False
    if _recently_sent(part.id):
        return False

    caption = _build_caption(part, request=request)
    photo_url = _first_image_url(part, request=request)

    message_id: Optional[int] = None

    if photo_url:
        raw = _fetch_image(photo_url)
        if raw is not None:
            processed = _square_crop_if_vertical(raw)
            if processed is not None:
                # вертикальная — отправляем обработанные байты (квадрат)
                message_id = _send_photo_with_bytes(processed, caption)
            else:
                # горизонтальная/квадрат — отправляем оригинал по URL
                message_id = _send_photo_by_url(photo_url, caption)
        else:
            # не скачалось — попробуем по URL
            message_id = _send_photo_by_url(photo_url, caption)

    if message_id is None:
        message_id = _send_message(caption)

    if message_id is not None:
        _set_message_id(part.id, message_id)
        _mark_sent(part.id)
        return True

    return False
