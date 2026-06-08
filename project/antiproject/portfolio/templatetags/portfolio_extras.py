from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    return value.split(arg)

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
