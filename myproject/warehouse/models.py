from django.db import models
from django.contrib.auth.models import User

class Part(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    part_type = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True, null=True)  # Поле для цвета
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='part_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.device} - {self.brand} - {self.model} - {self.part_type}"


