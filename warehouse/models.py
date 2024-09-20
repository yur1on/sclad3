from django.db import models
from django.contrib.auth.models import User

class Part(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    part_type = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)  # Установи auto_now_add=True

    def __str__(self):
        return f"{self.device} - {self.brand} - {self.model} - {self.part_type}"

class PartImage(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='part_images/')

    def __str__(self):
        return f"Image for {self.part}"

    def delete(self, using=None, keep_parents=False):
        self.image.delete()  # Удаляет файл изображения с сервера
        super().delete(using=using, keep_parents=keep_parents)

