import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import TelegramUser

TELEGRAM_BOT_TOKEN = "7285088265:AAF5P7f2uy33eRtWai4YkMHWYFZyHQhYt5k"

@csrf_exempt
def telegram_webhook(request):
    """ Получаем сообщения от Telegram и регистрируем chat_id пользователей """
    if request.method == "POST":
        data = request.json if request.content_type == "application/json" else None
        if data and "message" in data:
            chat_id = data["message"]["chat"]["id"]
            username = data["message"]["from"]["username"]
            text = data["message"]["text"]

            if text == "/start":
                user, created = User.objects.get_or_create(username=username)
                TelegramUser.objects.update_or_create(user=user, defaults={"chat_id": chat_id})

                send_telegram_message(chat_id, "✅ Вы зарегистрированы в системе! Теперь вы будете получать уведомления.")

        return JsonResponse({"status": "ok"})

def send_telegram_message(chat_id, text):
    """ Отправка сообщения конкретному пользователю в Telegram """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)



from django.urls import path
from .views import telegram_webhook

urlpatterns = [
    path("webhook/", telegram_webhook, name="telegram_webhook"),
]
