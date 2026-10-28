import ast
import ipaddress
import pathlib
import random
import unittest

from exercise import address_type, from_int, is_valid_ipv4, to_binary, to_int

SOURCE = pathlib.Path(__file__).with_name("exercise.py").read_text()


def random_address(rng):
    return ".".join(str(rng.randrange(256)) for _ in range(4))


class TestValid(unittest.TestCase):
    def test_valid(self):
        for text in ["192.168.1.10", "0.0.0.0", "255.255.255.255", "8.8.8.8", "10.0.0.1"]:
            self.assertTrue(is_valid_ipv4(text), text)

    def test_invalid(self):
        for text in ["256.1.1.1", "1.2.3", "1.2.3.4.5", "1.2.3.-4", "a.b.c.d", "1.2.3.", "", "1..2.3", " 1.2.3.4", "1.2.3.4 "]:
            self.assertFalse(is_valid_ipv4(text), repr(text))

    def test_leading_zeros(self):
        self.assertFalse(is_valid_ipv4("10.0.0.01"), "Leading zeros are not allowed: some programs read 010 as octal")
        self.assertTrue(is_valid_ipv4("10.0.0.0"), "A single 0 is fine")

    def test_matches_ipaddress_module(self):
        rng = random.Random(2)
        for _ in range(2000):
            parts = [rng.choice(["0", "7", "255", "256", "01", "300", "12", "x", ""]) for _ in range(rng.choice([3, 4, 4, 4, 5]))]
            text = ".".join(parts)
            try:
                ipaddress.IPv4Address(text)
                expected = True
            except ValueError:
                expected = False
            self.assertEqual(is_valid_ipv4(text), expected, repr(text))


class TestConversions(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(to_int("192.168.1.10"), 3232235786)
        self.assertEqual(from_int(3232235786), "192.168.1.10")
        self.assertEqual(to_int("0.0.0.0"), 0)
        self.assertEqual(from_int(4294967295), "255.255.255.255")
        self.assertEqual(to_binary("192.168.1.10"), "11000000.10101000.00000001.00001010")
        self.assertEqual(to_binary("10.0.0.1"), "00001010.00000000.00000000.00000001", "Pad each part to 8 digits")

    def test_random(self):
        rng = random.Random(3)
        for _ in range(2000):
            address = random_address(rng)
            self.assertEqual(to_int(address), int(ipaddress.IPv4Address(address)))
            self.assertEqual(from_int(to_int(address)), address)


class TestAddressType(unittest.TestCase):
    def test_types(self):
        cases = {
            "127.0.0.1": "loopback", "127.255.0.9": "loopback",
            "10.0.0.1": "private", "10.255.255.255": "private",
            "172.16.0.1": "private", "172.31.255.254": "private", "172.15.0.1": "public", "172.32.0.1": "public",
            "192.168.0.1": "private", "192.169.0.1": "public",
            "169.254.1.1": "link-local",
            "8.8.8.8": "public", "151.101.1.1": "public",
        }
        for address, expected in cases.items():
            self.assertEqual(address_type(address), expected, address)


class TestRules(unittest.TestCase):
    def test_no_ipaddress_module(self):
        for node in ast.walk(ast.parse(SOURCE)):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name for alias in node.names] + [getattr(node, "module", None)]
                self.assertNotIn("ipaddress", names, "Do it by hand: don't import the ipaddress module")


if __name__ == "__main__":
    unittest.main()
