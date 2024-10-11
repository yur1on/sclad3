from django.template.defaultfilters import register

from django import template

@register.filter
def to(value):
    return range(1, value + 1)





register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    return value.as_widget(attrs={'class': css_class})

