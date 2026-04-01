from django import template
register = template.Library()

@register.filter
def get_item(d, key):
    return d.get(key, 0) if isinstance(d, dict) else 0

@register.filter  
def multiply(value, arg):
    try: return float(value) * float(arg)
    except: return 0

@register.filter
def trim(value):
    return value.strip() if value else value
