import re
from numbers import Number
import copy


def fn_exists(fn):
    return fn in dir(__builtins__)


if not fn_exists('is_int'):
    def is_int(value):
        return True if re.match("[-+]?\d+$", str(value)) is not None else False

if not fn_exists('is_numeric'):
    def is_numeric(value):
        return True if isinstance(value, Number) or \
                       (isinstance(value, str) and value.isnumeric()) or \
                       is_float(value) else False

if not fn_exists('is_float'):
    def is_float(num):
        return isinstance(num, float) or (
                isinstance(num, str) and num.find('.') > 0 and is_int(num.replace('.', '', 1))
        )

if not fn_exists('to_numeric'):
    def to_numeric(num):
        if is_int(num):
            return int(num)
        elif is_float(num):
            return float(num)
        raise ValueError('Invalid number provided')

if not fn_exists('boarders_to_int'):
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
        values = data.copy()
        for part in key.split('.'):
            part = int(part) if is_int(part) else part
            if has_key(part, values):
                values = values[part]
            else:
                return False
        return True

if not fn_exists('has_key'):
    def has_key(key, data):
        try:
            data[key]
        except (KeyError, TypeError):
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

if not fn_exists('foreach'):
    def foreach(data):
        return data.items() if isinstance(data, dict) else enumerate(data)