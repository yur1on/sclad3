# tariff/utils.py
from warehouse.models import Part
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta

def check_parts_limit(user):
    """
    Проверяет, достиг ли пользователь лимита запчастей:
      - Бесплатный: 30 запчастей.
      - Lite: 500 запчастей.
      - Стандарт: 2000 запчастей.
      - Стандарт 2: 7000 запчастей.
      - Стандарт 3: 15000 запчастей.
      - Премиум: без ограничений.
    """
    if hasattr(user, 'profile'):
        tariff = user.profile.tariff
        if tariff == 'free':
            limit = 30
        elif tariff == 'lite':
            limit = 500
        elif tariff == 'standard':
            limit = 2000
        elif tariff == 'standard2':
            limit = 7000
        elif tariff == 'standard3':
            limit = 15000
        elif tariff == 'premium':
            return False  # Без ограничений
        parts_count = Part.objects.filter(user=user).count()
        return parts_count >= limit
    return False

def check_image_limit(user, images_count):
    """
    Для бесплатного тарифа: не более 1 изображения на запчасть.
    Для платных тарифов (Lite, Стандарт, Стандарт 2, Стандарт 3, Премиум): до 5 изображений.
    """
    if hasattr(user, 'profile') and user.profile.tariff == 'free':
        return images_count > 1
    return False  # Для платных тарифов ограничение до 5 уже в форме

def check_notifications_limit(user, limit=1):
    """
    Для бесплатного тарифа: лимит – 1 уведомление в сутки.
    Для платных тарифов (Lite, Стандарт, Стандарт 2, Стандарт 3, Премиум): без ограничений.
    """
    if hasattr(user, 'profile') and user.profile.tariff == 'free':
        now = timezone.now()
        start_period = now - timedelta(days=1)
        notifications_count = Notification.objects.filter(user=user, timestamp__gte=start_period).count()
        return notifications_count >= limit
    return False  # Для платных тарифов нет ограничений