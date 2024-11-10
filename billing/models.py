from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Subscription(models.Model):
    DURATION_CHOICES = [
        (1, '1 месяц'),
        (3, '3 месяца'),
        (6, '6 месяцев'),
        (12, '12 месяцев'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    duration = models.PositiveSmallIntegerField(choices=DURATION_CHOICES)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = timezone.now().date() + timezone.timedelta(days=30 * self.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - Подписка на {self.get_duration_display()}"
