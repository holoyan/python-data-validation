import unittest
from pyva import Validator


class TestIpRules(unittest.TestCase):

    def test_ipv4_and_ipv6_ips(self):

        ips = [
            '0.0.0.0',
            '9.255.255.255',
            '11.0.0.0',
            '126.255.255.255',
            '129.0.0.0',
            '169.253.255.255',
            '169.255.0.0',
            '172.15.255.255',
            '172.32.0.0',
            '191.0.1.255',
            '192.88.98.255',
            '192.88.100.0',
            '192.167.255.255',
            '192.169.0.0',
            '198.17.255.255',
            '223.255.255.255',
            '223.255.255.1',
            '1200:0000:AB00:1234:0000:2552:7777:1313',
            '21DA:D3:0:2F3B:2AA:FF:FE28:9C5A',
            'FE80:0000:0000:0000:0202:B3FF:FE1E:8329'
        ]

        for ip in ips:
            v = Validator(
                {
                    'ip': ip
                },
                {
                    'ip': 'ip'
                }
            )

            self.assertTrue(v.passes())

    def test_ipv4_and_ipv6_ips_fails(self):

        ips = [
            '1200:0000:AB00:1234:O000:2552:7777:1313',
            '[2001:db8:0:1]:80',
            'http://[2001:db8:0:1]:80',
            '256.0.0.0'
        ]

        for ip in ips:
            v = Validator(
                {
                    'ip': ip
                },
                {
                    'ip': 'ip'
                }
            )

            self.assertTrue(v.fails())

    def test_ipv4(self):

        ips = [
            '0.0.0.0',
            '9.255.255.255',
            '11.0.0.0',
            '126.255.255.255',
            '129.0.0.0',
            '169.253.255.255',
            '169.255.0.0',
            '172.15.255.255',
            '172.32.0.0',
            '191.0.1.255',
            '192.88.98.255',
            '192.88.100.0',
            '192.167.255.255',
            '192.169.0.0',
            '198.17.255.255',
            '223.255.255.255',
            '223.255.255.1',
        ]

        for ip in ips:
            v = Validator(
                {
                    'ip': ip
                },
                {
                    'ip': 'ipv4'
                }
            )

            self.assertTrue(v.passes())

    def test_ipv4_fails(self):

        ips = [
            '256.0.0.0',
            '1200::AB00:1234::2552:7777:1313',
            '1200:0000:AB00:1234:O000:2552:7777:1313',
            '[2001:db8:0:1]:80',
            'http://[2001:db8:0:1]:80',
            '1200:0000:AB00:1234:0000:2552:7777:1313',
            '21DA:D3:0:2F3B:2AA:FF:FE28:9C5A',
            'FE80:0000:0000:0000:0202:B3FF:FE1E:8329'
        ]

        for ip in ips:
            v = Validator(
                {
                    'ip': ip
                },
                {
                    'ip': 'ipv4'
                }
            )

            self.assertTrue(v.fails())
        
    def test_ipv6(self):

        ips = [
            '1200:0000:AB00:1234:0000:2552:7777:1313',
            '21DA:D3:0:2F3B:2AA:FF:FE28:9C5A',
            'FE80:0000:0000:0000:0202:B3FF:FE1E:8329'
        ]

        for ip in ips:
            v = Validator(
                {
                    'ip': ip
                },
                {
                    'ip': 'ipv6'
                }
            )

            self.assertTrue(v.passes())

    def test_ipv6_fails(self):

        ips = [
            '1200:0000:AB00:1234:O000:2552:7777:1313',
            '[2001:db8:0:1]:80',
            'http://[2001:db8:0:1]:80',
            '256.0.0.0',
            '0.0.0.0',
            '9.255.255.255',
            '11.0.0.0',
            '126.255.255.255',
            '129.0.0.0',
            '169.253.255.255',
        ]

        for ip in ips:
            v = Validator(
                {
                    'ip': ip
                },
                {
                    'ip': 'ipv6'
                }
            )

            self.assertTrue(v.fails())