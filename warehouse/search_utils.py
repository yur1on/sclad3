# search_utils.py
import re
from typing import Optional, Tuple

_ALNUM_TOKENS_RE = re.compile(r"[A-Za-z0-9]+")
_DIGIT_RE = re.compile(r"\d")


# ✅ ТВОЙ список брендов (из твоего JSON)
KNOWN_BRANDS_CANON = [
    "Apple", "Samsung", "Huawei", "Honor", "Xiaomi", "Poco", "Realme", "Vivo",
    "Tecno", "Infinix", "TCL", "Oppo", "Google", "OnePlus", "Alcatel", "Amigoo",
    "Archos", "Asus", "Black Shark", "BlackBerry", "BLU", "Cat", "Caterpillar",
    "Coolpad", "Cubot", "Doogee", "Elephone", "HTC", "Lenovo", "LG", "Meizu",
    "Micromax", "Motorola", "Nothing", "Nokia", "Nubia", "Oukitel", "Sharp",
    "Sony", "Wiko", "ZTE",
]

# быстрые структуры для поиска бренда в начале строки (с учётом пробелов/регистра)
_BRAND_BY_LOWER = {b.lower(): b for b in KNOWN_BRANDS_CANON}
_BRAND_BY_COMPACT = {re.sub(r"[\s\-]+", "", b.lower()): b for b in KNOWN_BRANDS_CANON}
_MAX_BRAND_WORDS = max(len(b.split()) for b in KNOWN_BRANDS_CANON)  # например 2 для "Black Shark"


def normalize_compact(text: str) -> str:
    """убираем пробелы/дефисы и lower"""
    t = (text or "").strip().lower()
    return re.sub(r"[\s\-]+", "", t)


def tokenize_alnum(text: str):
    return _ALNUM_TOKENS_RE.findall(text or "")


def is_modelish_token(tok: str) -> bool:
    tok = (tok or "").strip()
    return len(tok) >= 3 and bool(_DIGIT_RE.search(tok))


def note_regex_from_text(text: str) -> Optional[str]:
    tokens = [t for t in tokenize_alnum(text) if is_modelish_token(t)]
    if not tokens:
        return None
    escaped = [re.escape(t) for t in tokens]
    return r"\m(?:%s)\M" % "|".join(escaped)


def _detect_brand_prefix(tokens: list[str]) -> tuple[str, int]:
    """
    Пытаемся распознать бренд в начале запроса.
    Возвращает: (brand, used_token_count)
    """
    if not tokens:
        return "", 0

    # пробуем самое длинное совпадение: 2 слова, потом 1 слово
    for n in range(min(_MAX_BRAND_WORDS, len(tokens)), 0, -1):
        cand = " ".join(tokens[:n]).strip()
        cand_l = cand.lower()
        cand_c = normalize_compact(cand)

        if cand_l in _BRAND_BY_LOWER:
            return _BRAND_BY_LOWER[cand_l], n
        if cand_c in _BRAND_BY_COMPACT:
            return _BRAND_BY_COMPACT[cand_c], n

    return "", 0


def split_search_q(q: str, brand_in: str = "", model_in: str = "") -> Tuple[str, str, bool, str, str]:
    """
    ✅ Новая логика:
    - 1 слово => single_term (как раньше)
    - несколько:
        - если первый токен содержит цифры => бренд пустой, модель = вся строка
        - иначе бренд выделяем ТОЛЬКО если он распознан в списке брендов (в т.ч. "Black Shark")
        - если бренд не распознан => бренд пустой, модель = вся строка
    - если q пустой => совместимость со старыми параметрами brand/model
    """
    q = (q or "").strip()
    brand_in = (brand_in or "").strip()
    model_in = (model_in or "").strip()

    brand = ""
    model = ""
    single_term = False
    term = ""

    if q:
        parts = q.split()
        if len(parts) == 1:
            single_term = True
            term = parts[0]
            model = term
            return brand, model, single_term, term, q

        first = parts[0]
        if _DIGIT_RE.search(first):
            # "10 pro" -> это не бренд
            return "", q, False, "", q

        detected_brand, used = _detect_brand_prefix(parts)

        if detected_brand:
            brand = detected_brand
            model = " ".join(parts[used:]).strip()
            return brand, model, False, "", q

        # бренд не распознан => не режем строку
        return "", q, False, "", q

    # q пустой — совместимость
    brand = brand_in
    model = model_in
    if brand and model:
        q = f"{brand} {model}"
    elif brand:
        q = brand
    elif model:
        q = model

    return brand, model, False, "", q
