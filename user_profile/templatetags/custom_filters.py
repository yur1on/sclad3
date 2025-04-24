from django import template

register = template.Library()

@register.filter
def to(value):
    """Возвращает диапазон от 1 до value (включительно)."""
    return range(1, value + 1)

@register.filter(name='add_class')
def add_class(value, css_class):
    """Добавляет CSS-класс к виджету."""
    return value.as_widget(attrs={'class': css_class})

@register.filter
def subtract(value, arg):
    """Вычитает arg из value."""
    return value - arg

@register.filter
def get_day_word(days):
    """Возвращает правильное склонение слова 'день' в зависимости от числа."""
    try:
        days = int(days)  # Преобразуем в целое число, если это строка
        if days % 10 == 1 and days % 100 != 11:
            return "день"
        elif days % 10 in [2, 3, 4] and days % 100 not in [12, 13, 14]:
            return "дня"
        else:
            return "дней"
    except (ValueError, TypeError):
        return "дней"  # Возвращаем "дней" по умолчанию в случае ошибки