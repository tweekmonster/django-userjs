import six
import importlib

from django.conf import settings


class UserJSConfigurationError(Exception):
    pass


def _import_functions(name):
    funcs = getattr(settings, name, False)
    if not funcs:
        return False

    if not hasattr(funcs, '__iter__'):
        raise UserJSConfigurationError('%s must be iterable' % name)

    func_list = []
    for func in funcs:
        if six.callable(func):
            func_list.append(func)
            continue

        module, func = func.rsplit('.', 1)
        try:
            import_module = importlib.import_module(module)
        except ImportError:
            raise UserJSConfigurationError(
                '%s: Could not import module "%s"' % (module, name))

        try:
            import_func = getattr(import_module, func)
        except AttributeError:
            raise UserJSConfigurationError(
                '%s: Module %s does not have a funciton named "%s"'
                % (name, module, func))

        func_list.append(import_func)
    return tuple(func_list)


REQUIRE_CSRF = getattr(settings, 'USERJS_REQUIRE_CSRF', False)
IGNORE_EMPTY_VALUES = getattr(settings, 'USERJS_IGNORE_EMPTY_VALUES', False)
FIELDS = getattr(settings, 'USERJS_FIELDS', {})
POST_PROCESSORS = _import_functions('USERJS_POST_PROCESSORS')
JSON_HANDLERS = _import_functions('USERJS_JSON_HANDLERS')
