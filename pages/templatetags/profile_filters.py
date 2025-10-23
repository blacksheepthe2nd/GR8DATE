from django import template
from datetime import date

register = template.Library()

@register.filter
def calculate_age(dob):
    if dob:
        today = date.today()
        age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1
        return age
    return None

@register.filter
def split_interests(interests_string):
    if interests_string:
        return [interest.strip() for interest in interests_string.split(',')]
    return []
