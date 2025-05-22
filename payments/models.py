from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Допустимые типы тарифов
TARIFF_TYPE_CHOICES = (
    ('free', 'Бесплатный'),
    ('lite', 'Базовый'),
    ('standard', 'Стандартный'),
    ('standard2', 'Продвинутый'),
    ('standard3', 'Профессиональный'),
    ('premium', 'Неограниченный'),
)

class PaymentOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Номер заказа")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    duration = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Длительность подписки в месяцах (1, 3, 6, 12)",
        verbose_name="Длительность (месяцы)"
    )
    tariff_type = models.CharField(
        max_length=20,
        choices=TARIFF_TYPE_CHOICES,
        default='standard',
        verbose_name="Тип тарифа"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    invoice_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Номер счета")
    rrn = models.CharField(max_length=50, blank=True, null=True, verbose_name="RRN")
    transaction_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID транзакции")

    def __str__(self):
        return f"{self.order_number} - {self.user.username} - {self.status}"

    class Meta:
        verbose_name = "Заказ на оплату"
        verbose_name_plural = "Заказы на оплату"
