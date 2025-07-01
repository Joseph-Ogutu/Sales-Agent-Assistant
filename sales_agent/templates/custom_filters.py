import json
from django import template

register = template.Library()

@register.filter
def tojson(obj):
    return json.dumps(obj)