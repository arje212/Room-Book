from django import template

register = template.Library()

@register.filter
def to(value, end):
    """Custom filter to generate a range from value to end (inclusive)."""
    return range(value, end + 1)
