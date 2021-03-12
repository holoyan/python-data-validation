import unittest
from pyva.validator import Validator

class TestDependentRules(unittest.TestCase):

    def test_required_if(self):
        v = Validator({
            'user': {
                'name': 'John',
                'age': 26,
            }
        },{
            'user': 'required',
            'user.name': 'required_if:user.age,26'
        })

        self.assertTrue(v.passes())


    def test_required_if_fails(self):
        v = Validator({
            'user': {
                'age': 26,
            }
        },{
            'user': 'required',
            'user.name': 'required_if:user.age,26',
            'user.wife': 'required_if:user.age,26,30,69',
            'user.not_required': 'required_if:user.age,30,69',
        })

        self.assertTrue(not  v.passes())
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
        },{
            'user': 'required',
            'user.name': 'required_with:user.age,user.wife'
        })

        self.assertTrue(v.passes())

    def test_required_with_fails(self):
        v = Validator({
            'user': {
                'age': 20,
            }
        },{
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
        },{
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
        },{
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
        },{
            'user': 'required',
            'user.name': 'required_with_all:user.age,user.wife'
        })

        self.assertTrue(v.fails())
        self.assertTrue('user.name' in v.failed_rules)