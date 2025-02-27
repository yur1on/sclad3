from django.db import models
from django.contrib.auth.models import User

TARIFF_TYPE_CHOICES = (
    ('free', 'Бесплатный'),
    ('standard', 'Стандарт'),
    ('standard2', 'Стандарт 2'),  # Новый тариф
    ('premium', 'Премиум'),
)

class PaymentOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(default=1)  # количество периодов по 30 дней
    tariff_type = models.CharField(max_length=20, choices=TARIFF_TYPE_CHOICES, default='standard')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    rrn = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.order_number} - {self.user.username} - {self.status}"