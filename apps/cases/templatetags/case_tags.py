from django import template

register = template.Library()

@register.filter(name='split')
def split_filter(value, arg=','):
    """Splits a string by delimiter (defaults to comma)."""
    if not value:
        return []
    return [item.strip() for item in str(value).split(arg) if item.strip()]

@register.filter(name='replace')
def replace_filter(value, args):
    """Replaces occurrences of a substring. Format: |replace:"old,new" or |replace:"old" (removes old)"""
    if not value:
        return ""
    val_str = str(value)
    if isinstance(args, str):
        parts = args.split(',')
        if len(parts) >= 2:
            return val_str.replace(parts[0], parts[1])
        elif len(parts) == 1:
            return val_str.replace(parts[0], "")
    return val_str

@register.filter(name='get_item')
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
