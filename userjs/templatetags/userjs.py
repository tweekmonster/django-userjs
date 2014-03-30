from django import template
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def userjs_url(context, query_dict=None):
    url = reverse('userjs')
    if query_dict and isinstance(query_dict, dict):
        return '%s?%s' % (url, urlencode(query_dict, True))
    return url
