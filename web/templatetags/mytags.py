from django import template
from django.core.cache import cache
import os,json

register = template.Library()


@register.simple_tag
def cache_get(key):
    val = cache.get(key)
    if val is None:
        d = f"{os.path.dirname(__file__)}/lang_info.json"
        with open(d, 'r', encoding='utf-8') as f:
            content = ''.join(f.readlines())
        jsobj = json.loads(content)
        val=jsobj[key]['image_b64']
        cache.set(key, val, timeout=None)

    return val
