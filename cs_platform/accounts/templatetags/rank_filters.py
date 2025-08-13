from django import template

register = template.Library()

@register.filter
def rank_display(value):
    if not value:
        return ""
    return value.replace("_", " ").title().replace("Iii", "III").replace("Ii", "II").replace("I", "I")
