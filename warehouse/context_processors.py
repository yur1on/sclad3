
from .models import Part
from django.contrib.auth.models import User

def counts(request):
    return {
        'part_count': Part.objects.count(),
        'user_count': User.objects.count(),
    }

from notifications.models import Notification  # Если модель в user_profile

def unread_notifications(request):
    if request.user.is_authenticated:
        return {"unread_notifications": Notification.objects.filter(user=request.user, is_read=False).count()}
    return {"unread_notifications": 0}
