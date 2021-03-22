import unittest
from pyva import Validator


class MyTestCase(unittest.TestCase):
    def test_email_rule(self):

        emails = [
            'email@example.com',
            'firstname.lastname@example.com',
            'email@subdomain.example.com',
            'firstname+lastname@example.com',
            '1234567890@example.com',
            'email@example-one.com',
            '_______@example.com',
            'email@example.name',
            'email@example.museum',
            'email@example.co.jp',
            'firstname-lastname@example.com',
            'email@example.web',
            'email@subdomain.example.com',
            'email@[123.123.123.123]',
            '"email"@example.com',
        ]

        for email in emails:
            v = Validator(
                {
                    'email': email
                },
                {
                    'email': 'required|email'
                }
            )
            self.assertTrue(v.passes())

    def test_email_rule_fails(self):
        emails = [
            'Abc.example.com',
            'A@b@c@example.com',
            'a"b(c)d,e:f;g<h>i[j\k]l@example.com',
            'just"not"right@example.com',
            'thisis"not\allowed@example.com',
            'this\ still\"notallowed@example.com',
            'plainaddress',
            '#@%^%#$@#$@#.com',
            '@example.com',
            'Joe Smith < email@example.com >',
            'email.example.com',
            'email@example@example.com',
            '.email@example.com',
            'email.@example.com',
            'email..email@example.com',
            'email@example',
            '.333',
            '.44444',
            'email @ example..com',
            'Abc.',
            '.123 @ example.com',
            'email@123.123.123.123',
            'あいうえお@example.com',
            'email@-example.com',
            'email@example.com (Joe Smith)',

        ]

        for email in emails:
            v = Validator(
                {
                    'email': email
                },
                {
                    'email': 'required|email'
                }
            )
            self.assertTrue(v.fails())
