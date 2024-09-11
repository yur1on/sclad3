from django.template.defaultfilters import register

@register.filter
def to(value):
    return range(1, value + 1)

