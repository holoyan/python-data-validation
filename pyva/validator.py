import pyva.helpers as helpers
from pyva.closureValidationRule import ClosureValidationRule
from pyva.validationException import ValidationException
import random
import string
from pyva.Rules.ruleContract import RuleContract


class Validator:
    #     tmp
    # _file_rules = [
    #     'File', 'Image', 'Mimes', 'Mimetypes', 'Min',
    #     'Max', 'Size', 'Between', 'Dimensions',
    # ]

    _implicit_rules = [
        'required',
        'requiredWith',
        'requiredWithAll',
        'requiredWithout',
        'requiredWithoutAll',
        'requiredIf',
        'requiredUnless',
        'present',
    ]

    _dependent_rules = [
        'requiredWith', 'requiredWithAll', 'requiredWithout', 'requiredWithoutAll',
        'requiredIf', 'requiredUnless', 'confirmed', 'Same', 'Different', 'Unique',
        'Before', 'After', 'BeforeOrEqual', 'AfterOrEqual', 'Gt', 'Lt', 'Gte', 'Lte',
    ]

    _size_rules = ['size', 'between', 'min', 'max', 'gt', 'lt', 'gte', 'lte']

    numeric_rules = ['numeric', 'integer']

    def __init__(self, data, rules, messages=None):
        self.data = data
        self.initial_rules = rules.copy()
        self.rules = self.explode_rules(rules)
        self.messages = {} if messages is None else messages
        self._failed_rules = {}

    def explode_rules(self, rules: dict):
        rule_copy = rules.copy()
        for attribute, rule in rule_copy.items():
            split_rule = rule.split('|') if isinstance(rule, str) else rule
            rule_copy[attribute] = split_rule
            if '*' in attribute:
                rule_copy = {**rule_copy, **self._extract_wildcard_rules(attribute, split_rule, self.data)}
                del rule_copy[attribute]
        return rule_copy

    def _get_size(self, attribute, value):
        if helpers.is_int(value):
            return int(value)
        elif isinstance(value, str):
            return len(value)
        else:
            raise ValueError('Value must be instance of int or str')

    def _validate_required(self, attribute, value, *options):
        if value is None:
            return False
        elif isinstance(value, str) and len(''.join(value.strip())) < 1:
            return False
        elif hasattr(value, '__iter__') and len(value) < 1:
            return False

        return True

    def _validate_required_if(self, attribute, value, other_filed, other_value):
        return helpers.data_get(other_filed, self.data) == other_value

    def _validate_size(self, attribute, value, size):
        return self._get_size(attribute, value) == int(size)

    @helpers.boarders_to_int
    def _validate_between(self, attribute, value, left_board, right_board):
        return left_board <= self._get_size(attribute, value) <= right_board

    @helpers.boarders_to_int
    def _validate_min(self, attribute, value, left_board):
        return self._get_size(attribute, value) >= int(left_board)

    @helpers.boarders_to_int
    def _validate_max(self, attribute, value, right_board):
        return self._get_size(attribute, value) <= right_board

    @helpers.boarders_to_int
    def _validate_gt(self, attribute, value, left_board):
        return self._get_size(attribute, value) > left_board

    @helpers.boarders_to_int
    def _validate_gte(self, attribute, value, left_board):
        return self._get_size(attribute, value) >= left_board

    @helpers.boarders_to_int
    def _validate_lt(self, attribute, value, right_board):
        return self._get_size(attribute, value) < right_board

    @helpers.boarders_to_int
    def _validate_lte(self, attribute, value, right_board):
        return self._get_size(attribute, value) <= right_board

    def _validate_numeric(self, attribute, value):
        return helpers.is_numeric(value)

    def _validate_integer(self, attribute, value):
        return helpers.is_int(value)

    def _validate_list(self, attribute, value):
        return isinstance(value, list)

    def _validate_dict(self, attribute, value):
        return isinstance(value, dict)

    def get_value(self, attribute):
        return helpers.data_get(attribute, self.data)

    def _extract_wildcard_rules(self, attribute, rule, data):
        wildcard_rules = {}
        attr_list = attribute.split('*', maxsplit=1)
        attr = attr_list.pop(0).strip('.')
        nested_rules = attr_list[0]
        extracted_data = helpers.data_get(attr, data)

        for key, value in self._parse_data_for_loop(extracted_data):
            if '*' in nested_rules:
                print('nes')
                self._extract_wildcard_rules(attr + nested_rules, rule, extracted_data)
            else:
                wildcard_rules[attr + '.' + str(key) + nested_rules] = rule
        return wildcard_rules

    def _parse_data_for_loop(self, data):
        return data.items() if isinstance(data, dict) else enumerate(data)

    def _validate_attribute(self, attribute, rule):
        self._current_rule = rule
        value = self.get_value(attribute)

        if callable(rule):
            callback = ClosureValidationRule(rule)
            if not callback.passes(attribute, value):
                self._add_message(attribute, message=callback.message)
            return

        if isinstance(rule, RuleContract):
            return self._validate_with_custom_rule(rule, attribute, value)

        rule_suffix, param = self._parse_rules(rule)

        validatable = self.is_validatable(attribute, rule_suffix, value)

        method = getattr(self, '_validate_' + helpers.to_snake(rule_suffix))
        if validatable and not method(attribute, value, *param):
            self._add_message(attribute, rule_suffix)

    def _validate_with_custom_rule(self, rule, attribute, value):
        if not rule.passes(attribute, value):
            if helpers.method_exists(rule, 'message'):
                self._add_message(attribute, message=rule.message())
            else:
                self._add_message(attribute, rule.__class__.__name__)

    def is_validatable(self, attribute, rule, value):
        return rule in self._implicit_rules or helpers.data_has(attribute, self.data)  # attribute in self.data

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

    def _parse_rules(self, rules: str):

        parsed = rules.split(':', 1)
        method = parsed.pop(0)
        if len(parsed) == 0:
            return [method, []]
        return [method, parsed[0].split(',')]

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
        for attribute, rules in self.rules.items():
            for rule in rules:
                self._validate_attribute(attribute, rule)

                if self._should_stop(attribute):
                    break
        return len(self._failed_rules) == 0

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


class TestRule(RuleContract):

    def passes(self, attribute, value):
        return False