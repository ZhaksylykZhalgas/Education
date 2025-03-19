from django import template

register = template.Library()

@register.filter
def dict_key(value, key):
    """Возвращает значение по ключу из словаря."""
    return value.get(key)
