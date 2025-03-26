from django import template
from django.urls import reverse, resolve, NoReverseMatch

register = template.Library()

@register.simple_tag
def active_link(request, view_name, *args, **kwargs):
    try:
        url = reverse(view_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return ''
    
    if request.path.startswith(url):
        return 'active'
    return ''