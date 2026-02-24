from django import template

register = template.Library()

@register.filter
def until(start, end):
    """Generate range(start, end) para sa loop sa template"""
    return range(start, end)
