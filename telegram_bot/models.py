from django.db import models
from django.contrib.auth.models import User

class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.chat_id}"
