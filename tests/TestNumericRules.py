import unittest
from pyNet.validation.validator import Validator
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

    def test_numeric_fails(self):
        validation = Validator({
            'stringFloat': '4.5',
        },
        {
            'stringFloat': 'numeric',
        })

        self.assertTrue(validation.fails())


if __name__ == '__main__':
    unittest.main()
