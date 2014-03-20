import six
import json

from userjs.userjs_settings import JSON_HANDLERS


def _json_handlers(obj):
    """Extra handlers that JSON aren't able to parse.

    The only built-in conversion is for datetime.  User configured handlers
    are tried for other types.  If they all fail, raise TypeError.
    """
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif JSON_HANDLERS:
        for handler in JSON_HANDLERS:
            try:
                return handler(obj)
            except TypeError:
                pass
    raise TypeError('%s is not JSON serializable' % repr(obj))


def jsondumps(obj):
    """Creates a JSON string that can handle datetime objects.
    """
    return json.dumps(obj, separators=(',', ':'), default=_json_handlers)


def get_field_value(obj, field_name):
    """Get a value from an object

    This tries to get a value from an object that's similar to the way Django's
    queries work.  If it's unresolvable, return None instead of raising an
    exception.

    Not sure if there's a utility like this in Django that's available to use.
    """
    value = obj
    for field in field_name.split('__'):
        if not hasattr(value, field):
            return None
        value = getattr(value, field)
    if six.callable(value):
        return value()
    return value
