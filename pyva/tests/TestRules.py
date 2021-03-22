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
