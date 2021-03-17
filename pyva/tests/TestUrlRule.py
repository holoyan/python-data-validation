import unittest
from pyva import Validator


class TestUrlRule(unittest.TestCase):

    def test_valid_urls(self):
        urls = [
            'http://foo.com/blah_blah', 'http://foo.com/blah_blah_(wikipedia)', 'http://142.42.1.1/',
            'http://foo.com/blah_(wikipedia)_blah#cite-1', 'ftp://foo.bar/baz'
        ]

        for url in urls:
            v = Validator(
                {
                    'url': url
                },
                {
                    'url': 'url'
                }
            )

            self.assertTrue(v.passes())

    def test_invalid_urls(self):
        urls = [
            'http://a.b--c.de/', 'http://-error-.invalid/', 'http:///a',
            '//a', 'http://##'
        ]

        for url in urls:
            v = Validator(
                {
                    'url': url
                },
                {
                    'url': 'url'
                }
            )

            self.assertTrue(v.fails())