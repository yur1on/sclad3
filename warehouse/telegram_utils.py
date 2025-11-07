import requests
from user_profile.models import Profile

TELEGRAM_BOT_TOKEN = '7614699995:AAFIFb7LFtZPO3wBJnNQozKROJ6A-SKEql4'
CHAT_ID = '-1002649895374'

def get_device_with_ending(device):
    device = device.lower()
    if device == 'телефон':
        return device + 'а'
    elif device == 'планшет':
        return device + 'а'
    elif device == 'смарт-часы':
        return 'смарт-часов'
    else:
        return device

def send_new_part_notification(part):
    try:
        profile = Profile.objects.get(user=part.user)
        telegram_username = profile.telegram_username or part.user.username
    except Profile.DoesNotExist:
        telegram_username = part.user.username

    seller = f"@{telegram_username}" if telegram_username else part.user.username
    device_with_ending = get_device_with_ending(part.device)

    # Сообщение без эмоджи
    message = (
        f"<b>{part.part_type}</b>\n"
        f"для {device_with_ending}, <b>{part.brand} {part.display_model}</b>\n"
        f"Цена: <b>{part.price} руб</b>\n"
        f"Продавец: {seller}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки в Telegram: {e}")
