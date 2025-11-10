# warehouse/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Part
from .telegram_utils import send_new_part_notification

@receiver(post_save, sender=Part, dispatch_uid="warehouse.part.notify_new_part")
def notify_new_part(sender, instance, created, **kwargs):
    if created:
        # отправим только один раз при создании Part
        send_new_part_notification(instance)

