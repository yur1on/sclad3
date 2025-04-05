# warehouse/models.py
from django.db import models
from django.contrib.auth.models import User
import re
import uuid  # для генерации уникального кода

class Part(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=200)
    part_type = models.CharField(max_length=100)
    condition = models.CharField(max_length=50, blank=True, null=True)  # Новое поле для состояния
    color = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    chip_label = models.CharField(max_length=200, blank=True, null=True)  # Новое поле для маркировки микросхемы
    part_number = models.CharField("Номер запчасти", max_length=100, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device} - {self.brand} - {self.model} - {self.part_type}"

    # Свойство для отображения модели без содержимого в скобках
    @property
    def display_model(self):
        return re.sub(r'\s\(.*?\)$', '', self.model)

    def save(self, *args, **kwargs):
        if not self.part_number:
            # Можно автогенерировать номер, если он не введён (например, PART-XXXXXX)
            self.part_number = f'{uuid.uuid4().hex[:6].upper()}'
        super().save(*args, **kwargs)

    # Переопределяем метод delete для удаления связанных изображений
    def delete(self, using=None, keep_parents=False):
        for image in self.images.all():
            image.delete()
        super().delete(using=using, keep_parents=keep_parents)


class PartImage(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='part_images/')

    def __str__(self):
        return f"Image for {self.part}"

    # Переопределяем метод delete для удаления файла изображения с диска
    def delete(self, using=None, keep_parents=False):
        self.image.delete(save=False)
        super().delete(using=using, keep_parents=keep_parents)
