import six

from userjs import utils
from userjs.userjs_settings import (FIELDS, IGNORE_EMPTY_VALUES,
                                    POST_PROCESSORS, REQUIRE_CSRF)

from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie


def userjs_response(request):
    """Creates the actual script string.
    """
    fields = {
        'authenticated': request.user.is_authenticated(),
    }

    # No need to attract attention if this is a normal user.
    if request.user.is_staff:
        fields['staff'] = True
    if request.user.is_superuser:
        fields['superuser'] = True

    for k, v in six.iteritems(FIELDS):
        resolved = None
        if six.callable(v):
            resolved = v(request)
        elif isinstance(v, six.string_types):
            if v.startswith('str:'):
                resolved = v[4:]
            else:
                resolved = utils.get_field_value(request.user, v)
        else:
            resolved = v

        fields[k] = resolved

    if POST_PROCESSORS:
        for processor in POST_PROCESSORS:
            additional_fields = processor(request)
            if additional_fields:
                fields.update(additional_fields)

    if IGNORE_EMPTY_VALUES:
        fields = {k: v for k, v in six.iteritems(fields) if v}

    jsonp = request.GET.get('jsonp', '')

    js = utils.jsondumps(fields)
    if jsonp:
        js = '%s(%s);' % (jsonp, js)
    else:
        js = 'window.user=%s;' % js

    response = HttpResponse(js)
    response['content-length'] = len(js)
    response['content-type'] = 'text/javascript'
    return response


@ensure_csrf_cookie
def userjs_csrf(request):
    """View that ensures that a CSRF cookie is set.
    """
    return userjs_response(request)


def userjs(request):
    """Main userjs view.

    Returns userjs_csrf() if the settings or query string specify it.
    """
    if REQUIRE_CSRF or request.GET.get('csrf', False):
        return userjs_csrf(request)
    return userjs_response(request)
