import ast
import ipaddress
import pathlib
import random
import unittest

from exercise import broadcast_address, mask_to_prefix, network_address, prefix_to_mask, same_network, usable_hosts

SOURCE = pathlib.Path(__file__).with_name("exercise.py").read_text()


class TestMasks(unittest.TestCase):
    def test_prefix_to_mask(self):
        self.assertEqual(prefix_to_mask(24), "255.255.255.0")
        self.assertEqual(prefix_to_mask(20), "255.255.240.0")
        self.assertEqual(prefix_to_mask(32), "255.255.255.255")
        self.assertEqual(prefix_to_mask(0), "0.0.0.0")

    def test_mask_to_prefix(self):
        self.assertEqual(mask_to_prefix("255.255.252.0"), 22)
        self.assertEqual(mask_to_prefix("255.0.0.0"), 8)

    def test_all_prefixes(self):
        for prefix in range(33):
            mask = str(ipaddress.IPv4Network(f"0.0.0.0/{prefix}").netmask)
            self.assertEqual(prefix_to_mask(prefix), mask)
            self.assertEqual(mask_to_prefix(mask), prefix)


class TestNetworks(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(network_address("192.168.1.130/25"), "192.168.1.128")
        self.assertEqual(broadcast_address("192.168.1.130/25"), "192.168.1.255")
        self.assertEqual(network_address("10.20.30.40/16"), "10.20.0.0")
        self.assertEqual(broadcast_address("10.20.30.40/16"), "10.20.255.255")

    def test_random(self):
        rng = random.Random(4)
        for _ in range(2000):
            address = ".".join(str(rng.randrange(256)) for _ in range(4))
            prefix = rng.randrange(33)
            net = ipaddress.IPv4Network(f"{address}/{prefix}", strict=False)
            self.assertEqual(network_address(f"{address}/{prefix}"), str(net.network_address), f"{address}/{prefix}")
            self.assertEqual(broadcast_address(f"{address}/{prefix}"), str(net.broadcast_address), f"{address}/{prefix}")


class TestHosts(unittest.TestCase):
    def test_usable(self):
        self.assertEqual(usable_hosts(24), 254)
        self.assertEqual(usable_hosts(26), 62)
        self.assertEqual(usable_hosts(30), 2)
        self.assertEqual(usable_hosts(16), 65534)

    def test_tiny_networks(self):
        self.assertEqual(usable_hosts(31), 2, "A /31 is a link between two devices: both addresses are usable")
        self.assertEqual(usable_hosts(32), 1, "A /32 is a single address")


class TestSameNetwork(unittest.TestCase):
    def test_examples(self):
        self.assertTrue(same_network("10.0.4.20", "10.0.7.200", 22))
        self.assertFalse(same_network("10.0.4.20", "10.0.8.1", 22))
        self.assertTrue(same_network("192.168.1.5", "192.168.1.250", 24))
        self.assertFalse(same_network("192.168.1.5", "192.168.2.5", 24))

    def test_random(self):
        rng = random.Random(5)
        for _ in range(2000):
            a = ".".join(str(rng.randrange(256)) for _ in range(4))
            b = ".".join(str(rng.randrange(256)) if i > 1 else a.split(".")[i] for i in range(4))
            prefix = rng.randrange(8, 33)
            expected = ipaddress.IPv4Address(b) in ipaddress.IPv4Network(f"{a}/{prefix}", strict=False)
            self.assertEqual(same_network(a, b, prefix), expected, f"{a} {b} /{prefix}")


class TestRules(unittest.TestCase):
    def test_no_ipaddress_module(self):
        for node in ast.walk(ast.parse(SOURCE)):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name for alias in node.names] + [getattr(node, "module", None)]
                self.assertNotIn("ipaddress", names, "Do it with bits: don't import the ipaddress module")


if __name__ == "__main__":
    unittest.main()
