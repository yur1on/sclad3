from django.db import models
from django.contrib.auth.models import User

# Список областей Беларуси для выбора в профиле
BELARUS_REGIONS = [
    ('Минская область', 'Минская область'),
    ('Гомельская область', 'Гомельская область'),
    ('Гродненская область', 'Гродненская область'),
    ('Брестская область', 'Брестская область'),
    ('Могилевская область', 'Могилевская область'),
    ('Витебская область', 'Витебская область'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    region = models.CharField(max_length=100, choices=BELARUS_REGIONS, blank=True, null=True)  # Добавляем поле область
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.city} - {self.phone}"

    @property
    def average_rating(self):
        reviews = self.user.received_reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 5  # Возвращаем 5, если нет отзывов


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveSmallIntegerField()  # Рейтинг от 1 до 5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review from {self.reviewer} to {self.user} - {self.rating} stars"
