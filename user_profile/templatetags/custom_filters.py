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