# booking_filters.py
from django import template

register = template.Library()

@register.filter
def filter_status(bookings, status):
    return [b for b in bookings if b.status == status]