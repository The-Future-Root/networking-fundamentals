import ssl
import unittest

from exercise import EXAMPLE_CERT, certificate_problems, days_left, dns_names, hostname_matches, issuer_name


def when(text):
    return ssl.cert_time_to_seconds(text)


BAKERY_CERT = {
    "subject": ((("commonName", "rosiesbakery.example"),),),
    "issuer": ((("countryName", "US"),), (("organizationName", "Let's Encrypt"),), (("commonName", "R11"),)),
    "notBefore": "Mar  1 00:00:00 2026 GMT",
    "notAfter": "May 30 23:59:59 2026 GMT",
    "subjectAltName": (("DNS", "rosiesbakery.example"), ("DNS", "www.rosiesbakery.example")),
}


class TestNames(unittest.TestCase):
    def test_dns_names(self):
        self.assertEqual(dns_names(EXAMPLE_CERT), ["example.com", "*.example.com"])
        self.assertEqual(dns_names(BAKERY_CERT), ["rosiesbakery.example", "www.rosiesbakery.example"])

    def test_only_dns_entries(self):
        cert = {"subjectAltName": (("DNS", "a.example"), ("IP Address", "192.0.2.1"), ("DNS", "b.example"))}
        self.assertEqual(dns_names(cert), ["a.example", "b.example"])

    def test_issuer(self):
        self.assertEqual(issuer_name(EXAMPLE_CERT), "Cloudflare TLS Issuing ECC CA 3")
        self.assertEqual(issuer_name(BAKERY_CERT), "R11")


class TestHostnameMatches(unittest.TestCase):
    def test_exact(self):
        self.assertTrue(hostname_matches("example.com", "example.com"))
        self.assertTrue(hostname_matches("example.com", "EXAMPLE.com"), "Host names aren't case-sensitive")
        self.assertFalse(hostname_matches("example.com", "example.org"))
        self.assertFalse(hostname_matches("example.com", "www.example.com"))

    def test_wildcard(self):
        self.assertTrue(hostname_matches("*.example.com", "www.example.com"))
        self.assertTrue(hostname_matches("*.example.com", "SHOP.example.com"))
        self.assertFalse(hostname_matches("*.example.com", "example.com"), "A wildcard needs one label in front: it doesn't cover the bare domain")
        self.assertFalse(hostname_matches("*.example.com", "a.b.example.com"), "A wildcard covers exactly one label")
        self.assertFalse(hostname_matches("*.example.com", "wwwexample.com"))
        self.assertFalse(hostname_matches("*.example.com", ".example.com"))


class TestDaysLeft(unittest.TestCase):
    def test_days(self):
        self.assertEqual(days_left(EXAMPLE_CERT, when("Oct 26 12:00:00 2026 GMT")), 60)
        self.assertEqual(days_left(BAKERY_CERT, when("May 29 23:59:59 2026 GMT")), 1)
        self.assertEqual(days_left(BAKERY_CERT, when("May 30 12:00:00 2026 GMT")), 0, "Less than a day left counts as 0")

    def test_expired(self):
        self.assertLess(days_left(BAKERY_CERT, when("Jun 10 00:00:00 2026 GMT")), 0)


class TestProblems(unittest.TestCase):
    def test_fine(self):
        now = when("Oct 26 12:00:00 2026 GMT")
        self.assertEqual(certificate_problems(EXAMPLE_CERT, "example.com", now), [])
        self.assertEqual(certificate_problems(EXAMPLE_CERT, "www.example.com", now), [])

    def test_wrong_host(self):
        now = when("Oct 26 12:00:00 2026 GMT")
        self.assertEqual(certificate_problems(EXAMPLE_CERT, "example.org", now), ["wrong host name"])
        self.assertEqual(certificate_problems(EXAMPLE_CERT, "shop.www.example.com", now), ["wrong host name"])

    def test_dates(self):
        self.assertEqual(certificate_problems(BAKERY_CERT, "rosiesbakery.example", when("Feb 20 10:00:00 2026 GMT")), ["not valid yet"])
        self.assertEqual(certificate_problems(BAKERY_CERT, "rosiesbakery.example", when("Jul  1 10:00:00 2026 GMT")), ["expired"])

    def test_several(self):
        self.assertEqual(certificate_problems(BAKERY_CERT, "shop.rosiesbakery.example", when("Jul  1 10:00:00 2026 GMT")), ["expired", "wrong host name"])


if __name__ == "__main__":
    unittest.main()
