from django import template
from django.db.models import Func
register = template.Library()

@register.filter
def ordinal(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    if 10 <= value % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
    return f"{value}{suffix}"

class Round(Func):
    function = 'ROUND'
    arity = 2