import unittest
from pyva import Validator


class TestDependentRules(unittest.TestCase):

    def test_required_if(self):
        v = Validator({
            'user': {
                'name': 'John',
                'age': 26,
            }
        }, {
            'user': 'required',
            'user.name': 'required_if:user.age,26'
        })

        self.assertTrue(v.passes())

    def test_required_if_fails(self):
        v = Validator({
            'user': {
                'age': 26,
            }
        }, {
            'user': 'required',
            'user.name': 'required_if:user.age,26',
            'user.wife': 'required_if:user.age,26,30,69',
            'user.not_required': 'required_if:user.age,30,69',
        })

        self.assertTrue(not v.passes())
        self.assertTrue('user.name' in v.failed_rules)
        self.assertTrue('user.wife' in v.failed_rules)
        self.assertTrue('user.not_required' not in v.failed_rules)

    def test_required_with(self):
        v = Validator({
            'user': {
                'name': 'John',
                'age': 26,
                'wife': {
                    'name': 'Anna',
                    'age': 20
                }
            }
        }, {
            'user': 'required',
            'user.name': 'required_with:user.age,user.wife'
        })

        self.assertTrue(v.passes())

    def test_required_with_fails(self):
        v = Validator({
            'user': {
                'age': 20,
            }
        }, {
            'user': 'required',
            'user.name': 'required_with:user.age',
            'user.wife': 'required_with:user.age'
        })

        self.assertTrue(not v.passes())
        self.assertTrue('user.name' in v.failed_rules)
        self.assertTrue('user.wife' in v.failed_rules)

    def test_required_with_all(self):
        v = Validator({
            'user': {
                'name': 'John',
                'age': 26,
                'wife': {
                    'name': 'Anna',
                    'age': 20
                }
            }
        }, {
            'user': 'required',
            'user.name': 'required_with_all:user.age,user.wife'
        })

        self.assertTrue(v.passes())

    def test_required_with_all_pass_without_all_params(self):
        v = Validator({
            'user': {
                'wife': {
                    'name': 'Anna',
                    'age': 20
                }
            }
        }, {
            'user': 'required',
            'user.name': 'required_with_all:user.age,user.wife'
        })

        self.assertTrue(v.passes())

    def test_required_with_all_fails(self):
        v = Validator({
            'user': {
                'age': 26,
                'wife': {
                    'name': 'Anna',
                    'age': 20
                }
            }
        }, {
            'user': 'required',
            'user.name': 'required_with_all:user.age,user.wife'
        })

        self.assertTrue(v.fails())
        self.assertTrue('user.name' in v.failed_rules)

    def test_required_without(self):
        v = Validator({
            'user': {
                'name': 'John',
                'age': None,
                'wife': {
                    'name': 'Anna',
                    'age': 20
                }
            }
        }, {
            'user': 'required',
            'user.name': 'required_without:user.age,user.wife'
        })

        self.assertTrue(v.passes())

    def test_required_without_fails(self):
        v = Validator({
            'user': {
                'age': None,
            }
        }, {
            'user': 'required',
            'user.name': 'required_without:user.age'
        })

        self.assertTrue(v.fails())
        self.assertTrue('user.name' in v.failed_rules)

    def test_required_without_all(self):
        v = Validator({
            'user': {
                'age': 25,
                'wife': {
                    'name': 'Anna',
                    'age': 20
                }
            }
        }, {
            'user': 'required',
            'user.name': 'required_without:user.age,user.wife'
        })

        self.assertTrue(v.passes())

    def test_required_without_all_fails(self):
        v = Validator({
            'user': {
                'age': None,
            }
        }, {
            'user': 'required',
            'user.name': 'required_without_all:user.age,user.wife'
        })

        self.assertTrue(v.fails())
        self.assertTrue('user.name' in v.failed_rules)

    def test_required_without_all_fails_with_empty_data(self):
        v = Validator({
            'user': {
            }
        }, {
            'user': 'required',
            'user.name': 'required_without_all:user.age,user.wife'
        })

        self.assertTrue(v.fails())
        self.assertTrue('user.name' in v.failed_rules)

    def test_required_unless(self):
        v = Validator({
            'user': {
                'age': 25
            }
        }, {
            'user': 'required',
            'user.name': 'required_unless:user.age,25'
        })

        self.assertTrue(v.passes())

    def test_required_unless_fails(self):
        v = Validator({
            'user': {
                'age': 25
            }
        }, {
            'user': 'required',
            'user.name': 'required_unless:user.age:26,27'
        })

        self.assertTrue(v.fails())
        self.assertTrue('user.name' in v.failed_rules)

    def test_present(self):
        v = Validator({
            'user': {
                'age': 25
            }
        }, {
            'user': 'required',
            'user.age': 'present'
        })

        self.assertTrue(v.passes())

    def test_present_fails(self):
        v = Validator({
            'user': {
            }
        }, {
            'user': 'required',
            'user.age': 'present'
        })

        self.assertTrue(v.fails())
        self.assertTrue('user.age' in v.failed_rules)
