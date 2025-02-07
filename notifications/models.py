from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    text = models.TextField(max_length=255)  # Ограничение на 255 символов
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Уведомление от {self.sender} для {self.user} ({self.timestamp})"
