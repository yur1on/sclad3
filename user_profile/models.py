from django.db import models
from django.contrib.auth.models import User
from warehouse.models import Part

# Список областей Беларуси для выбора в профиле
BELARUS_REGIONS = [
    ('Минская область', 'Минская область'),
    ('Гомельская область', 'Гомельская область'),
    ('Гродненская область', 'Гродненская область'),
    ('Брестская область', 'Брестская область'),
    ('Могилевская область', 'Могилевская область'),
    ('Витебская область', 'Витебская область'),
]

# Выбор тарифного плана
TARIFF_CHOICES = (
    ('free', 'Беспла́тный'),
    ('lite', 'Базовый'),
    ('standard', 'Cтандартный'),
    ('standard2', 'Продвинутый'),
    ('standard3', 'Профессиональный'),
    ('premium', 'Неограниченный'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Полное имя")
    subscription_start = models.DateTimeField(blank=True, null=True, verbose_name="Начало подписки")
    subscription_end = models.DateTimeField(blank=True, null=True, verbose_name="Окончание подписки")
    phone = models.CharField(max_length=15)
    region = models.CharField(max_length=100, choices=BELARUS_REGIONS, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    workshop_name = models.CharField(max_length=100, blank=True, null=True)
    delivery_methods = models.TextField(max_length=300, blank=True, null=True)
    receive_notifications = models.BooleanField(default=True, verbose_name="Получать уведомления")
    tariff = models.CharField(max_length=10, choices=TARIFF_CHOICES, default='free', verbose_name="Тарифный план")
    email_confirmed = models.BooleanField(default=False, verbose_name="Email подтвержден")  # Новое поле

    def __str__(self):
        return f"{self.full_name or self.user.username} - {self.city} - {self.phone}"

    @property
    def average_rating(self):
        reviews = self.user.received_reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 5

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveSmallIntegerField()  # Рейтинг от 1 до 5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.reviewer} к {self.user} - {self.rating} звезд"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.part}"
