import pyva.helpers as helpers
from pyva.closureValidationRule import ClosureValidationRule
from pyva import ValidationException
import random
import string
from pyva import RuleContract
import re


class Validator:
    _implicit_rules = [
        'required',
        'required_with',
        'required_with_all',
        'required_without',
        'required_without_all',
        'required_if',
        'required_unless',
        'present',
    ]

    _dependent_rules = [
        'required_with', 'required_with_all', 'required_without', 'required_without_all',
        'required_if', 'required_unless', 'confirmed', 'same', 'different', 'unique',
        'before', 'after', 'before_or_equal', 'after_or_equal', 'gt', 'lt', 'gte', 'lte',
    ]

    _size_rules = ['size', 'between', 'min', 'max', 'gt', 'lt', 'gte', 'lte']

    _compiled_regexes = None

    _numeric_rules = ['numeric', 'integer']

    _regex_rules = ['re']

    __passed = None

    def __init__(self, data, rules, messages=None):
        self.data = data
        self.initial_rules = rules.copy()
        self.messages = {} if messages is None else messages
        self._failed_rules = {}
        self._implicit_attributes = {}
        self.rules = self.explode_rules(rules)

    def explode_rules(self, rules: dict):
        rule_copy = rules.copy()
        for attribute, rule in rule_copy.items():
            # split rules into list
            split_rule = rule.split('|') if isinstance(rule, str) else rule
            rule_copy[attribute] = split_rule
            # if there is * then we are gone iterate over data and create all nested rules
            if '*' in attribute:
                nested_attributes = self._extract_wildcard_rules(attribute, split_rule)
                if attribute not in self._implicit_attributes:
                    self._implicit_attributes[attribute] = []
                self._implicit_attributes[attribute] = list(nested_attributes.keys())
                rule_copy = {**rule_copy, **nested_attributes}
                del rule_copy[attribute]
        return rule_copy

    def __require_parameter_count(self, count, params, rule):
        if len(params) < count:
            raise ValueError("Validation rule {} requires at least {} parameters.".format(rule, count))

    def _extract_wildcard_rules(self, attribute, rule):
        '''

        recursively extract nested attributes

        :param attribute:
        :param rule:
        :param data:
        :return:
        '''
        wildcard_rules = {}
        # users.*.family.*.child
        # extract data for first * and do it recursively
        attr_list = attribute.split('*', maxsplit=1)

        attr = attr_list.pop(0).strip('.')
        nested_rules = attr_list[0]
        extracted_data = helpers.data_get(attr, self.data)

        if not extracted_data:
            wildcard_rules[attribute.replace('*', '0')] = rule
            return wildcard_rules

        for key, value in helpers.foreach(extracted_data):
            if '*' in nested_rules:
                wildcard_rules = {**wildcard_rules,
                                  **self._extract_wildcard_rules(attr + '.' + str(key) + nested_rules, rule)}
            else:
                wildcard_rules[attr + '.' + str(key) + nested_rules] = rule
        return wildcard_rules

    def _get_size(self, attribute, value):
        if helpers.is_numeric(value):
            return helpers.to_numeric(value)
        elif isinstance(value, str) or hasattr(value, '__len__'):
            return len(value)
        else:
            raise ValueError('Value must be instance of int or str or must implement __len__ method')

    def _validate_required(self, attribute, value, *options):
        if value is None:
            return False
        elif isinstance(value, str) and len(''.join(value.strip())) < 1:
            return False
        elif hasattr(value, '__len__') and len(value) < 1:
            return False

        return True

    def _validate_required_if(self, attribute, value, *other_params):
        self.__require_parameter_count(2, other_params, 'required_if')

        other_value = helpers.data_get(other_params[0], self.data)
        values = other_params[1:]

        if isinstance(other_value, bool):
            values = list(map(lambda val: True if val == 'True' else False if val == 'False' else val))

        if other_value in values:
            return self._validate_required(attribute, value)

        return True

    def _validate_required_unless(self, attribute, value, *other_params):
        self.__require_parameter_count(2, other_params, 'required_unless')
        other_value = helpers.data_get(other_params[0], self.data)
        values = other_params[1:]

        if isinstance(other_value, bool):
            values = list(map(lambda val: True if val == 'True' else False if val == 'False' else val))

        # if other value in list of rules values then validate as required
        if other_value not in values:
            return self._validate_required(attribute, value)

        return True

    def _validate_present(self, attribute, value, *other_params):
        return helpers.data_has(attribute, self.data)

    def _validate_required_with(self, attribute, value, *other_fields):
        if self._any_required(other_fields):
            return self._validate_required(attribute, value)
        return True

    def _validate_required_with_all(self, attribute, value, *other_fields):
        if not self._any_failing_required(other_fields):
            return self._validate_required(attribute, value)
        return True

    def _validate_required_without(self, attribute, value, *other_fields):
        if self._any_failing_required(other_fields):
            return self._validate_required(attribute, value)
        return True

    def _validate_required_without_all(self, attribute, value, *other_fields):
        if self._all_failing_required(other_fields):
            return self._validate_required(attribute, value)
        return True

    def _any_failing_required(self, params):
        for att in params:
            if not self._validate_required(att, helpers.data_get(att, self.data)):
                return True
        return False

    def _all_failing_required(self, params):
        for att in params:
            if self._validate_required(att, helpers.data_get(att, self.data)):
                return False
        return True

    def _any_required(self, params):
        for att in params:
            if self._validate_required(att, helpers.data_get(att, self.data)):
                return True
        return False

    def _validate_size(self, attribute, value, *size):
        self.__require_parameter_count(1, size, 'size')
        return self._get_size(attribute, value) == int(size[0])

    @helpers.boarders_to_int
    def _validate_between(self, attribute, value, left_board, right_board):
        return left_board <= self._get_size(attribute, value) <= right_board

    @helpers.boarders_to_int
    def _validate_min(self, attribute, value, *left_board):
        self.__require_parameter_count(1, left_board, 'min')
        return self._get_size(attribute, value) >= left_board[0]

    @helpers.boarders_to_int
    def _validate_max(self, attribute, value, *right_board):
        self.__require_parameter_count(1, right_board, 'max')
        return self._get_size(attribute, value) <= right_board[0]

    def _validate_gt(self, attribute, value, *other_filed):
        self.__require_parameter_count(1, other_filed, 'gt')
        other_value = helpers.data_get(other_filed[0], self.data)

        # if values are numeric cast and check
        if helpers.is_numeric(value) and helpers.is_numeric(other_value):
            value = helpers.to_numeric(value)
            other_value = helpers.to_numeric(other_value)
            return value > other_value

        # if they are not same type return False
        if type(value) != type(other_value):
            return False

        # check sizes
        return self._get_size(attribute, value) > self._get_size(other_filed[0], other_value)

    def _validate_gte(self, attribute, value, *other_filed):
        self.__require_parameter_count(1, other_filed, 'gte')
        other_value = helpers.data_get(other_filed[0], self.data)

        # if values are numeric cast and check
        if helpers.is_numeric(value) and helpers.is_numeric(other_value):
            value = helpers.to_numeric(value)
            other_value = helpers.to_numeric(other_value)
            return value >= other_value

        # if they are not same type return False
        if type(value) != type(other_value):
            return False

        # check sizes
        return self._get_size(attribute, value) >= self._get_size(other_filed[0], other_value)

    def _validate_lt(self, attribute, value, *other_filed):
        self.__require_parameter_count(1, other_filed, 'lt')
        other_value = helpers.data_get(other_filed[0], self.data)

        # if values are numeric cast and check
        if helpers.is_numeric(value) and helpers.is_numeric(other_value):
            value = helpers.to_numeric(value)
            other_value = helpers.to_numeric(other_value)
            return value < other_value

        # if they are not same type return False
        if type(value) != type(other_value):
            return False

        # check sizes
        return self._get_size(attribute, value) < self._get_size(other_filed[0], other_value)

    def _validate_lte(self, attribute, value, *other_filed):
        self.__require_parameter_count(1, other_filed, 'lte')
        other_value = helpers.data_get(other_filed[0], self.data)

        # if values are numeric cast and check
        if helpers.is_numeric(value) and helpers.is_numeric(other_value):
            value = helpers.to_numeric(value)
            other_value = helpers.to_numeric(other_value)
            return value <= other_value

        # if they are not same type return False
        if type(value) != type(other_value):
            return False

        # check sizes
        return self._get_size(attribute, value) <= self._get_size(other_filed[0], other_value)

    def _validate_numeric(self, attribute, value):
        return helpers.is_numeric(value)

    def _validate_integer(self, attribute, value):
        return helpers.is_int(value)

    def _validate_list(self, attribute, value):
        return isinstance(value, list)

    def _validate_dict(self, attribute, value):
        return isinstance(value, dict)

    def __compile_regex(self, pattern):
        if self._compiled_regexes is None:
            self._compiled_regexes = {}
        if pattern not in self._compiled_regexes:
            self._compiled_regexes[pattern] = re.compile(pattern)

    def _validate_email(self, attribute, value):
        pattern = """^(?!(?:(?:\\x22?\\x5C[\\x00-\\x7E]\\x22?)|(?:\\x22?[^\\x5C\\x22]\\x22?)){255,})(?!(?:(?:\\x22?\\x5C[\\x00-\\x7E]\\x22?)|(?:\\x22?[^\\x5C\\x22]\\x22?)){65,}@)(?:(?:[\\x21\\x23-\\x27\\x2A\\x2B\\x2D\\x2F-\\x39\\x3D\\x3F\\x5E-\\x7E]+)|(?:\\x22(?:[\\x01-\\x08\\x0B\\x0C\\x0E-\\x1F\\x21\\x23-\\x5B\\x5D-\\x7F]|(?:\\x5C[\\x00-\\x7F]))*\\x22))(?:\\.(?:(?:[\\x21\\x23-\\x27\\x2A\\x2B\\x2D\\x2F-\\x39\\x3D\\x3F\\x5E-\\x7E]+)|(?:\\x22(?:[\\x01-\\x08\\x0B\\x0C\\x0E-\\x1F\\x21\\x23-\\x5B\\x5D-\\x7F]|(?:\\x5C[\\x00-\\x7F]))*\\x22)))*@(?:(?:(?!.*[^.]{64,})(?:(?:(?:xn--)?[a-z0-9]+(?:-[a-z0-9]+)*\\.){1,126}){1,}(?:(?:[a-z][a-z0-9]*)|(?:(?:xn--)[a-z0-9]+))(?:-[a-z0-9]+)*)|(?:\\[(?:(?:IPv6:(?:(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){7})|(?:(?!(?:.*[a-f0-9][:\\]]){7,})(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,5})?::(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,5})?)))|(?:(?:IPv6:(?:(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){5}:)|(?:(?!(?:.*[a-f0-9]:){5,})(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,3})?::(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,3}:)?)))?(?:(?:25[0-5])|(?:2[0-4][0-9])|(?:1[0-9]{2})|(?:[1-9]?[0-9]))(?:\\.(?:(?:25[0-5])|(?:2[0-4][0-9])|(?:1[0-9]{2})|(?:[1-9]?[0-9]))){3}))\\]))$"""
        self.__compile_regex(pattern)
        return self._compiled_regexes[pattern].search(value) is not None

    def _validate_url(self, attribute, value):
        pattern = """^(https?|ftp)://(-\.)?([^\s/?\.#-]+\.?)+(/[^\s]*)?$"""
        self.__compile_regex(pattern)

        return self._compiled_regexes[pattern].search(value) is not None

    def _validate_ip(self, attribute, value):
        pattern = """((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))"""
        self.__compile_regex(pattern)

        return self._compiled_regexes[pattern].search(value) is not None

    def _validate_ipv4(self, attribute, value):
        pattern = """^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"""
        self.__compile_regex(pattern)

        return self._compiled_regexes[pattern].search(value) is not None

    def _validate_ipv6(self, attribute, value):
        pattern = """^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"""
        self.__compile_regex(pattern)

        return self._compiled_regexes[pattern].search(value) is not None

    def _validate_in(self, attribute, value, *other_values):
        return value in other_values

    def _validate_string(self, attribute, value):
        return isinstance(value, str)

    def _validate_nullable(self, *empty_params):
        return True

    def _validate_re(self, attribute, value, *re):
        self.__compile_regex(re[0])
        return self._compiled_regexes[re[0]].search(value) is not None

    def _validate_date(self, attribute, value, *other):
        return helpers.is_date(value)

    def get_value(self, attribute):
        return helpers.data_get(attribute, self.data)

    def __validate_attribute(self, attribute, rule):
        self._current_rule = rule
        value = self.get_value(attribute)

        if callable(rule):
            callback = ClosureValidationRule(rule)
            if not callback.passes(attribute, value):
                self._add_message(attribute, message=callback.message)
            return

        if isinstance(rule, RuleContract):
            return self._validate_with_custom_rule(rule, attribute, value)

        rule_suffix, params = self._parse_rules(rule)

        if rule_suffix in self._dependent_rules:
            keys = self._attribute_keys(attribute)
            if keys:
                params = self._replace_asterisks(params, keys)

        params = self._to_numeric_if_needs(params)

        validatable = self.is_validatable(attribute, rule_suffix, value)

        method = getattr(self, '_validate_' + rule_suffix)
        if validatable and not method(attribute, value, *params):
            self._add_message(attribute, rule_suffix)

    def _to_numeric_if_needs(self, params):
        return list(map(lambda val: helpers.to_numeric(val) if helpers.is_numeric(val) else val, params))

    def _attribute_keys(self, attribute: str):
        original_attribute = attribute
        for unparsed, parsed in helpers.foreach(self._implicit_attributes):
            if attribute in parsed:
                original_attribute = unparsed

        pattern = re.escape(original_attribute).replace('\*', '([^\.]+)')
        searches = re.findall(pattern, attribute, re.DOTALL)

        if searches:
            if isinstance(searches[0], tuple):
                searches = list(searches[0])
        return searches

    def _replace_asterisks(self, params, keys):
        parsed_params = []
        for attr in params:
            attr = attr.replace('*', '{}')
            parsed_params.append(attr.format(*keys))
        return parsed_params

    def _validate_with_custom_rule(self, rule, attribute, value):
        if not rule.passes(attribute, value):
            if helpers.method_exists(rule, 'message'):
                self._add_message(attribute, message=rule.message(attribute, value))
            else:
                self._add_message(attribute, rule.__class__.__name__)

    def is_validatable(self, attribute, rule, value):
        if rule in self._implicit_rules:
            return True

        data = helpers.data_get(attribute, self.data)

        if self.has_rule(attribute, 'nullable') == False and data is not None:
            return True

        if helpers.data_has(attribute, self.data) and data is not None:
            return True

        return False

    def _add_message(self, attribute, rule_suffix=None, message=None):
        if attribute not in self._failed_rules:
            self._failed_rules[attribute] = []

        if message:
            self._failed_rules[attribute].append(message)
        else:
            concrete_rule_message_key = "{}.{}".format(attribute, rule_suffix)
            self._failed_rules[attribute].append(
                self.messages[concrete_rule_message_key] if concrete_rule_message_key in self.messages else
                self.messages[attribute] if attribute in self.messages else 'validation.{}'.format(rule_suffix)
            )

    def has_rule(self, attribute, rule):
        return rule in self._get_rule(attribute)

    def _get_rule(self, attribute):

        if attribute not in self.rules:
            return []

        rules = []
        for rule in self.rules[attribute]:
            if callable(rule) or isinstance(rule, RuleContract):
                rules.append(rule)
            else:
                rule_suffix, params = self._parse_rules(rule)
                rules.append(rule_suffix)

        return rules

    def _parse_rules(self, rules: str):

        if isinstance(rules, list):
            return [rules[0], rules[1:]]

        parsed = rules.split(':', 1)
        rule = parsed.pop(0)
        if len(parsed) == 0:
            return [rule, []]

        if rule in self._regex_rules:
            return [rule, parsed]

        return [rule, parsed[0].split(',')]

    def _should_stop(self, attribute):
        '''
        In case the attribute has any rule that indicates that the field is required
        and that rule already failed then we should stop validation at this point
        as now there is no point in calling other rules with this field empty.
        :param attribute:
        :return: bool
        '''
        return True if self._current_rule in self._implicit_rules and attribute in self._failed_rules else False

    @property
    def failed_rules(self):
        return self._failed_rules

    def passes(self):

        if self.__passed is not None:
            return self.__passed

        for attribute, rules in self.rules.items():
            for rule in rules:
                self.__validate_attribute(attribute, rule)

                if self._should_stop(attribute):
                    break

        self.__passed = len(self._failed_rules) == 0
        return self.__passed

    def validated(self):
        if self.fails():
            raise ValidationException(self)

        result = {}
        for attribute, rules in self.rules.items():
            missing_data = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))
            value = helpers.data_get(attribute, self.data, missing_data)

            if value != missing_data:
                helpers.data_set(result, attribute, value)
        return result

    def fails(self):
        return not self.passes()
