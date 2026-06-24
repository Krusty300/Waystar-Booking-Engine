from django import template

register = template.Library()

@register.filter
def yes_no(value):
    """Convert boolean to Yes/No"""
    return 'Yes' if value else 'No'

@register.filter
def checkmark(value):
    """Convert boolean to checkmark"""
    return '✅' if value else '❌'

@register.filter
def get_icon(value):
    """Get icon for amenity"""
    if value:
        return value
    return '📌'