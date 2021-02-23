import unittest
from validator import Validator


class TestSizeRules(unittest.TestCase):
    def test_size(self):
        validation = Validator({
            'age': 10,
            'bill': -6,
            'count': 0
        }, {
            'age': 'size:10',
            'bill': 'size:-6',
            'count': 'size:0'
        })

        self.assertTrue(validation.passes())

    def test_size_must_fail(self):
        validation = Validator({
            'age': 5,
            'bill': -7,
            'count': 0
        }, {
            'age': 'size:10',
            'bill': 'size:-6',
            'count': 'size:0'
        })

        self.assertTrue(validation.fails())

    def test_between(self):
        validation = Validator({
            'age': 11,
            'bill': -3200
        }, {
            'age': 'between:10,100',
            'bill': 'between:-3200,0'
        })

        self.assertTrue(validation.passes())

    def test_between_must_fail(self):
        validation = Validator({
            'age': 9,
            'bill': -3300
        }, {
            'age': 'between:10,100',
            'bill': 'between:-3200,0'
        })

        self.assertTrue(validation.fails())
        self.assertTrue('age' in validation.failed_rules)
        self.assertTrue('bill' in validation.failed_rules)

    def test_min(self):
        validation = Validator({
            'age': 9,
            'height': 185
        }, {
            'age': 'min:1',
            'height': 'min:1'
        })

        self.assertTrue(validation.passes())

    def test_min_fails(self):
        validation = Validator({
            'age': 2,
            'height': -185
        }, {
            'age': 'min:1',
            'height': 'min:1'
        })

        self.assertTrue(validation.fails())
        self.assertTrue('height' in validation.failed_rules)

    def test_max(self):
        validation = Validator({
            'age': 9,
            'height': 185
        }, {
            'age': 'max:100',
            'height': 'max:250'
        })

        self.assertTrue(validation.passes())

    def test_max_fails(self):
        validation = Validator({
            'age': 9,
            'height': 251
        }, {
            'age': 'max:100',
            'height': 'max:250'
        })

        self.assertTrue(validation.fails())
        self.assertTrue('height' in validation.failed_rules)

    def test_gt(self):
        validation = Validator({
            'age': 22,
            'height': 185
        }, {
            'age': 'gt:18',
            'height': 'gt:1'
        })

        self.assertTrue(validation.passes())

    def test_gt_fail(self):
        validation = Validator({
            'age': 17,
            'height': 185
        }, {
            'age': 'gt:18',
            'height': 'gt:185'
        })

        self.assertTrue(validation.fails())
        self.assertTrue('age' in validation.failed_rules)
        self.assertTrue('height' in validation.failed_rules)

    def test_lt(self):
        validation = Validator({
            'age': 10,
            'height': 185
        }, {
            'age': 'lt:18',
            'height': 'lt:250'
        })

        self.assertTrue(validation.passes())

    def test_lt_fail(self):
        validation = Validator({
            'age': 17,
            'height': 185
        }, {
            'age': 'lt:17',
            'height': 'lt:200'
        })

        self.assertTrue(validation.fails())
        self.assertTrue('age' in validation.failed_rules)
        self.assertTrue('height' not in validation.failed_rules)

    def test_gte(self):
        validation = Validator({
            'age': 10,
            'height': 185
        }, {
            'age': 'gte:10',
            'height': 'gte:100'
        })

        self.assertTrue(validation.passes())

    def test_gte_fails(self):
        validation = Validator({
            'age': 9,
            'height': 185
        }, {
            'age': 'gte:10',
            'height': 'gte:100'
        })

        self.assertTrue(validation.fails())
        self.assertTrue('age' in validation.failed_rules)
        self.assertTrue('height' not in validation.failed_rules)

    def test_lte(self):
        validation = Validator({
            'age': 10,
            'height': 90
        }, {
            'age': 'lte:10',
            'height': 'lte:100'
        })

        self.assertTrue(validation.passes())

    def test_lte_fails(self):
        validation = Validator({
            'age': 10,
            'height': 185
        }, {
            'age': 'lte:10',
            'height': 'lte:100'
        })

        self.assertTrue(validation.fails())
        self.assertTrue('age' not in validation.failed_rules)
        self.assertTrue('height' in validation.failed_rules)


if __name__ == '__main__':
    unittest.main()
