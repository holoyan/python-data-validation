import unittest
from pyva import Validator
import decimal
import fractions


class TestNumericRules(unittest.TestCase):

    def test_integer(self):
        validation = Validator({
            'age': 10,
            'height': 120
        },
        {
            'age': 'integer',
            'height': 'integer'
        })

        self.assertTrue(validation.passes())

    def test_integer_fails(self):
        validation = Validator({
            'age': 10.5,
            'height': 120
        },
        {
            'age': 'integer',
            'height': 'integer'
        })

        self.assertTrue(validation.fails())
        self.assertTrue('age' in validation.failed_rules)

    def test_numeric(self):
        validation = Validator({
            'int': 10,
            'float': 0.5,
            'decimal': decimal.Decimal(3),
            'fraction': fractions.Fraction(2, 1),
            'complex': 2 + 4j,
            'stringInteger': '4',
            'stringFloat': '5.9'
        },
        {
            'int': 'numeric',
            'float': 'numeric',
            'decimal': 'numeric',
            'fraction': 'numeric',
            'complex': 'numeric',
            'stringInteger': 'numeric',
        })

        self.assertTrue(validation.passes())

    def test_nested_data_min(self):
        validation = Validator({
            'user': {
                'name': 'john',
                'age': 20,
                'children': [
                    {
                        'name': 'jr1',
                        'age': 3
                    },
                    {
                        'name': 'jr2',
                        'age': 7
                    }
                ]
            },
        },
        {
            'user': 'dict',
            'user.name': 'required|min:4',
            'user.age': 'required|min:18',
            'user.children.*.name': 'required|max:10',
            'user.children.*.age': 'required|max:10|min:2'
        })

        self.assertTrue(validation.passes())

    def test_nested_data_min_fails(self):
        validation = Validator({
            'user': {
                'name': 'john',
                'age': 20,
            },
        },
        {
            'user': 'dict',
            'user.name': 'required|min:4',
            'user.age': 'required|min:28',
        })

        self.assertTrue(validation.fails())
        self.assertTrue('user.age' in validation.failed_rules)


if __name__ == '__main__':
    unittest.main()
