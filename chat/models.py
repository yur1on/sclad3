
from django.db import models
from django.contrib.auth.models import User
from warehouse.models import Part

class Chat(models.Model):
    user1 = models.ForeignKey(User, related_name='chats_initiated', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='chats_received', on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE, null=True, blank=True)
    hidden_for = models.ManyToManyField(User, related_name="hidden_chats", blank=True)

    def is_hidden_for(self, user):
        return self.hidden_for.filter(id=user.id).exists()


    def __str__(self):
        return f"Chat between {self.user1} and {self.user2}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=5000)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # ✅ Добавлено поле

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"