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
      - Для тарифа Стандарт 2: 10000 запчастей.
      - Для премиум тарифа: нет ограничений.
    """
    if hasattr(user, 'profile'):
        tariff = user.profile.tariff
        if tariff == 'free':
            limit = 30
        elif tariff == 'standard':
            limit = 1000
        elif tariff == 'standard2':
            limit = 10000  # Лимит для Стандарт 2
        elif tariff == 'premium':
            return False  # Без ограничений
        parts_count = Part.objects.filter(user=user).count()
        return parts_count >= limit
    return False

def check_image_limit(user, images_count):
    """
    Для бесплатного тарифа: разрешается не более 1 изображения на запчасть.
    Для платных тарифов (Стандарт, Стандарт 2, Премиум) допускается до 5 изображений.
    """
    if hasattr(user, 'profile') and user.profile.tariff == 'free':
        return images_count > 1
    return False  # Для Стандарт, Стандарт 2 и Премиум ограничение до 5 уже в форме

def check_notifications_limit(user, limit=1):
    """
    Для бесплатного тарифа: лимит – 1 уведомление в сутки.
    Для платных тарифов (Стандарт, Стандарт 2, Премиум) ограничения отсутствуют.
    """
    if hasattr(user, 'profile') and user.profile.tariff == 'free':
        now = timezone.now()
        start_period = now - timedelta(days=1)
        notifications_count = Notification.objects.filter(user=user, timestamp__gte=start_period).count()
        return notifications_count >= limit
    return False  # Для Стандарт, Стандарт 2 и Премиум нет ограничений