from django.db import models

class Advertisement(models.Model):
    partner_name = models.CharField("Название партнёра", max_length=100)
    image = models.ImageField("Баннер", upload_to='ads/')
    url = models.URLField("Ссылка на сайт партнёра")
    active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    def __str__(self):
        return self.partner_name
