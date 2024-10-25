# в templatetags/device_filters.py
from django import template

register = template.Library()

@register.filter
def device_declension(device_name):
    declensions = {
        "Телефон": "Телефона",
        "Планшет": "Планшета",
        "Ноутбук": "Ноутбука",
        "Компьютер": "Компьютера",
        "Смарт-часы": "Смарт-часов",
        "Телевизор": "Телевизора"
    }
    return declensions.get(device_name, device_name)  # Возвращаем склонённое название или исходное, если не найдено
