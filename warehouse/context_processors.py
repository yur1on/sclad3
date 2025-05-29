# warehouse/context_processors.py
from .models import Part
from django.contrib.auth.models import User
from django.utils import timezone
from notifications.models import Notification  # Если модель в user_profile
from django.conf import settings
def counts(request):
    return {
        'part_count': Part.objects.count(),
        'user_count': User.objects.count(),
    }

def unread_notifications(request):
    if request.user.is_authenticated:
        return {"unread_notifications": Notification.objects.filter(user=request.user, is_read=False).count()}
    return {"unread_notifications": 0}

def get_day_word(days):
    """Функция для выбора правильного склонения слова 'день'"""
    if days % 10 == 1 and days % 100 != 11:
        return "день"
    elif days % 10 in [2, 3, 4] and days % 100 not in [12, 13, 14]:
        return "дня"
    else:
        return "дней"

def subscription_status(request):
    subscription_notification = None
    days_left = None
    subscription_expired = False

    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.subscription_end:
            days_left = (profile.subscription_end - timezone.now()).days
            if days_left < 0:
                subscription_notification = "Ваша подписка истекла!"
                subscription_expired = True
            elif days_left < 7 and days_left >= 0:
                day_word = get_day_word(days_left)
                subscription_notification = f"Подписка истекает через {days_left} {day_word}"

    return {
        'subscription_notification': subscription_notification,
        'days_left': days_left,
        'subscription_expired': subscription_expired,
    }



def debug_mode(request):
    return {
        'debug': settings.DEBUG
    }