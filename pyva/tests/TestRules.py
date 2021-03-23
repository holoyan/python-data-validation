import unittest
from pyva import Validator


class MyTestCase(unittest.TestCase):
    def test_regex(self):

        passwords = [
            'AA!45a.aa',
            'ABl49#kghjgdf',
            'Akl9!!CB69*#kdf'
        ]

        for p in passwords:
            # print(p)
            v = Validator(
                {
                    'password': p
                },
                {
                    'password': 're:^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,15}$',
                }
            )

            self.assertTrue(v.passes())

    def test_regex_fail(self):

        inv = [
            'AA45aa',
            '45aaa',
            'AA@!5',
            'aa@!5aaa'
        ]

        for p in inv:
            v = Validator(
                {
                    'password': p
                },
                {
                    'password': 're:^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,15}$',
                }
            )

            self.assertTrue(v.fails())

    def test_multiple_rules(self):
        v = Validator(
            {
                'name': 'john',
                'email': 'john@example.com',
                'birth_date': '1985-08-25 15:12:02',
                'height': 190
            },
            {
                'name': 'required|string|min:3|max:16',
                'email': 'required|string|email|min:3|max:32',
                'birth_date': 'required|date',
                'height': 'required|integer|max:250'
            }
        )

        self.assertTrue(v.passes())