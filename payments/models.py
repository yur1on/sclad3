from django.db import models
from django.contrib.auth.models import User

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=100)  # Название плана (например, "Basic" или "Premium")
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Стоимость подписки
    is_active = models.BooleanField(default=False)  # Активна ли подписка (будет активирована после успешной оплаты)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan_name}"

class Payment(models.Model):
    """
    Модель для хранения информации о платеже.
    """
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "В ожидании"), ("paid", "Оплачено"), ("failed", "Ошибка")],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"
