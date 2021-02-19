import pyNet.validation.helpers as helper


class Validator:
    #     tmp
    # _file_rules = [
    #     'File', 'Image', 'Mimes', 'Mimetypes', 'Min',
    #     'Max', 'Size', 'Between', 'Dimensions',
    # ]

    _implicit_rules = [
        'required',
        # 'Filled',
        'RequiredWith',
        'RequiredWithAll',
        'RequiredWithout',
        'RequiredWithoutAll',
        'RequiredIf',
        'RequiredUnless',
        # 'Accepted',
        'Present',
    ]

    _dependent_rules = [
        'RequiredWith', 'RequiredWithAll', 'RequiredWithout', 'RequiredWithoutAll',
        'RequiredIf', 'RequiredUnless', 'Confirmed', 'Same', 'Different', 'Unique',
        'Before', 'After', 'BeforeOrEqual', 'AfterOrEqual', 'Gt', 'Lt', 'Gte', 'Lte',
    ]

    _size_rules = ['size', 'between', 'min', 'max', 'gt', 'lt', 'gte', 'lte']

    numeric_rules = ['numeric', 'integer']

    def __init__(self, data, rules, messages=None):
        self.data = data
        self.initial_rules = rules
        self.rules = self.explode_rules(rules)
        self.messages = messages
        self._failed_rules = {}

    def explode_rules(self, rules: dict):
        rule_copy = rules.copy()
        for key, rule in rule_copy.items():
            rule_copy[key] = rule.split('|') if isinstance(rule, str) else rule
        return rule_copy

    def _get_size(self, attribute, value):
        if helper.is_int(value):
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

    def _validate_size(self, attribute, value, size):
        return self._get_size(attribute, value) == int(size)

    @helper.boarders_to_int
    def _validate_between(self, attribute, value, left_board, right_board):
        return left_board <= self._get_size(attribute, value) <= right_board

    @helper.boarders_to_int
    def _validate_min(self, attribute, value, left_board):
        return self._get_size(attribute, value) >= int(left_board)

    @helper.boarders_to_int
    def _validate_max(self, attribute, value, right_board):
        return self._get_size(attribute, value) <= right_board

    @helper.boarders_to_int
    def _validate_gt(self, attribute, value, left_board):
        return self._get_size(attribute, value) > left_board

    @helper.boarders_to_int
    def _validate_gte(self, attribute, value, left_board):
        return self._get_size(attribute, value) >= left_board

    @helper.boarders_to_int
    def _validate_lt(self, attribute, value, right_board):
        return self._get_size(attribute, value) < right_board

    @helper.boarders_to_int
    def _validate_lte(self, attribute, value, right_board):
        return self._get_size(attribute, value) <= right_board

    def _validate_numeric(self, attribute, value):
        return helper.is_numeric(value)

    def _validate_integer(self, attribute, value):
        return helper.is_int(value)

    def get_value(self, attribute):
        return self.data.get(attribute)

    def _validate_attribute(self, attribute, rule):
        self._current_rule = rule

        rule_suffix, param = self._parse_rules(rule)
        value = self.get_value(attribute)

        method = getattr(self, '_validate_' + rule_suffix)
        if not method(attribute, value, *param):
            self._add_message(attribute, rule_suffix, param)

    def _add_message(self, attribute, rule_suffix, params):
        if attribute not in self._failed_rules:
            self._failed_rules[attribute] = []
        self._failed_rules[attribute].append({
            rule_suffix: 'validation.{} must be {} '.format(attribute, rule_suffix) + ', '.join(params)
        })

    def _parse_rules(self, rules: str):

        parsed = rules.split(':', 1)
        method = parsed.pop(0)
        if len(parsed) == 0:
            return [method, []]
        return [method, parsed[0].split(',')]

    def should_stop(self, attribute):
        return True if self._current_rule in self._implicit_rules and attribute in self._failed_rules else False

    @property
    def failed_rules(self):
        return self._failed_rules

    def passes(self):
        for attribute, rules in self.rules.items():
            for rule in rules:
                self._validate_attribute(attribute, rule)

                if self.should_stop(attribute):
                    break
        return len(self._failed_rules) == 0

    def fails(self):
        return not self.passes()