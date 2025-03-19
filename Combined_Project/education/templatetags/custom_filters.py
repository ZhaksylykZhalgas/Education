from django import template

register = template.Library()

@register.filter
def to_list(value):
    """Converts an iterable or string to a list."""
    if hasattr(value, '__iter__') and not isinstance(value, str):
        return list(value)
    elif isinstance(value, str):
        return list(value)
    return [value]
