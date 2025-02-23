# tariff/utils.py
from warehouse.models import Part
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta

def check_parts_limit(user):
    """
    Проверяет, достиг ли пользователь лимита запчастей.
      - Для бесплатного тарифа: 30 запчастей.
      - Для стандартного тарифа: 1000 запчастей.
      - Для премиум тарифа: нет ограничений.
    """
    if hasattr(user, 'profile'):
        tariff = user.profile.tariff
        if tariff == 'free':
            limit = 30
        elif tariff == 'standard':
            limit = 1000
        elif tariff == 'premium':
            return False  # без ограничений
        parts_count = Part.objects.filter(user=user).count()
        return parts_count >= limit
    return False

def check_image_limit(user, images_count):
    """
    Для бесплатного тарифа: разрешается не более 1 изображения на запчасть.
    Для платных тарифов допускается до 5 (при этом форма уже позволяет до 5).
    """
    if hasattr(user, 'profile') and user.profile.tariff == 'free':
        return images_count > 1
    return False

def check_notifications_limit(user, limit=1):
    """
    Для бесплатного тарифа: лимит – 1 уведомление в сутки.
    Для платных тарифов ограничения отсутствуют.
    """
    if hasattr(user, 'profile') and user.profile.tariff == 'free':
        now = timezone.now()
        start_period = now - timedelta(days=1)
        notifications_count = Notification.objects.filter(user=user, timestamp__gte=start_period).count()
        return notifications_count >= limit
    return False
