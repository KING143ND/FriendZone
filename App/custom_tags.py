from django import template

register = template.Library()

@register.filter
def format_date(value):
    return value.strftime("%d %b %Y")

@register.simple_tag
def display_date(date, last_date):
    if date != last_date:
        return True
    return False
