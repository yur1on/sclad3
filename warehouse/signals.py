# warehouse/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Part
from .telegram_utils import send_new_part_notification

@receiver(post_save, sender=Part)
def notify_new_part(sender, instance, created, **kwargs):
    if created:
        send_new_part_notification(instance)
