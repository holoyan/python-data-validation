from pyva import RuleContract
from pyva import Validator


class DivisibleBy(RuleContract):

    def __init__(self, divide_to):
        self.divide_to = divide_to

    def passes(self, attribute, value):
        if self.divide_to == 0:
            return False

        return value % self.divide_to == 0

    def message(self, attribute, value):
        return "{} is not divisible by {}".format(value, self.divide_to)


v = Validator(
    {
        'someNumber': 9
    },
    {
        'someNumber': [DivisibleBy(4)]
    }
)

if v.passes():
    print(v.validated())
else:
    print(v.failed_rules)  # prints {'someNumber': ['9 is not divisible to 4']}
