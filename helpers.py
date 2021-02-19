import re
from numbers import Number

if 'is_int' not in dir(__builtins__):
    def is_int(value):
        return True if re.match("[-+]?\d+$", str(value)) is not None else False


if 'is_numeric' not in dir(__builtins__):
    def is_numeric(value):
        return True if isinstance(value, Number) or (isinstance(value, str) and value.isnumeric()) else False


def boarders_to_int(fn):
    def wrapper_to_int(self, *args):
        list_args = list(args)
        return fn(self, list_args.pop(0), list_args.pop(0), *list(map(int, list_args)))

    return wrapper_to_int