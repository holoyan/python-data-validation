import re
from numbers import Number
import copy


def fn_exists(fn):
    return fn in dir(__builtins__)


if 'is_int' not in dir(__builtins__):
    def is_int(value):
        return True if re.match("[-+]?\d+$", str(value)) is not None else False

if 'is_numeric' not in dir(__builtins__):
    def is_numeric(value):
        return True if isinstance(value, Number) or (isinstance(value, str) and value.isnumeric()) else False

if 'boarders_to_int' not in dir(__builtins__):
    def boarders_to_int(fn):
        def wrapper_to_int(self, *args):
            list_args = list(args)
            return fn(self, list_args.pop(0), list_args.pop(0), *list(map(int, list_args)))

        return wrapper_to_int

if not fn_exists('data_get'):
    def data_get(key, data, default=None):
        '''
        key = user.name
        data = {
            user: {
                name:'john'
            }
        }

        key = users.0.name
        data = {
            users: [
                {
                    name:'john1'
                },
                {
                    name:'john2'
                }
            ]
        }

        :param default:
        :param key:
        :param data:
        :return:
        '''
        if key in data:
            return data[key]
        try:
            values = data.copy()
            for part in key.split('.'):
                casted_index = int(part) if is_int(part) else part
                if has_key(casted_index, values):
                    values = values[casted_index]
                else:
                    return default
            return values
        except:
            pass
        return default

if not fn_exists('data_has'):
    def data_has(key, data):
        '''
        key = user.name
        data = {
            user: {
                name:'john'
            }
        }

        key = users.0.name
        data = {
            users: [
                {
                    name:'john1'
                },
                {
                    name:'john2'
                }
            ]
        }

        :param default:
        :param key:
        :param data:
        :return:
        '''
        if key in data:
            return True
        try:
            values = data.copy()
            for part in key.split('.'):
                casted_index = int(part) if is_int(part) else part
                if has_key(casted_index, values):
                    values = values[casted_index]
                else:
                    return False
        except:
            pass
        return True

if not fn_exists('has_key'):
    def has_key(key, data):
        try:
            data[key]
        except IndexError:
            return False
        return True

if not fn_exists('data_set'):
    def data_set(data, keys, value):
        segments = keys.split('.')
        while len(segments) > 1:
            segment = segments.pop(0)

            if is_int(segment):
                segment = int(segment)
                if not has_key(segment, data):
                    data[segment] = {}
            elif segment not in data:
                data[segment] = {}
            data = data[segment]
        index = segments.pop(0)
        index = int(index) if is_int(index) else index
        data[index] = copy.deepcopy(value)

if not fn_exists('to_snake'):
    def to_snake(str):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', str).lower()

if not fn_exists('method_exists'):
    def method_exists(obj, method):
        return callable(getattr(obj, method, None))