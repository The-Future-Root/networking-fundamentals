import unittest

from exercise import MAX_HOPS, ZONE, DnsCache, lowest_ttl, resolve


class TestResolve(unittest.TestCase):
    def test_a_record(self):
        self.assertEqual(resolve(ZONE, "rosiesbakery.example"), ["203.0.113.10"])
        self.assertEqual(resolve(ZONE, "mail.rosiesbakery.example"), ["203.0.113.25"])

    def test_cname(self):
        self.assertEqual(resolve(ZONE, "www.rosiesbakery.example"), ["203.0.113.10"], "Follow the CNAME to the real name, then return its A records")

    def test_cname_to_several_addresses(self):
        self.assertEqual(resolve(ZONE, "shop.rosiesbakery.example"), ["198.51.100.20", "198.51.100.21"])

    def test_chain(self):
        zone = {"a.example": [("CNAME", "b.example", 60)], "b.example": [("CNAME", "c.example", 60)], "c.example": [("A", "192.0.2.1", 60)]}
        self.assertEqual(resolve(zone, "a.example"), ["192.0.2.1"])

    def test_no_such_name(self):
        with self.assertRaises(LookupError):
            resolve(ZONE, "nope.rosiesbakery.example")

    def test_cname_to_missing_name(self):
        zone = {"old.example": [("CNAME", "gone.example", 60)]}
        with self.assertRaises(LookupError):
            resolve(zone, "old.example")

    def test_loop(self):
        with self.assertRaises(ValueError, msg="A CNAME loop must stop with ValueError, not run forever"):
            resolve(ZONE, "loop-a.example")

    def test_long_chain_allowed(self):
        zone = {f"n{i}.example": [("CNAME", f"n{i + 1}.example", 60)] for i in range(MAX_HOPS - 1)}
        zone[f"n{MAX_HOPS - 1}.example"] = [("A", "192.0.2.9", 60)]
        self.assertEqual(resolve(zone, "n0.example"), ["192.0.2.9"], f"A chain of {MAX_HOPS} names is fine")

    def test_name_with_no_a_record(self):
        zone = {"mailonly.example": [("MX", "mail.example", 60)]}
        self.assertEqual(resolve(zone, "mailonly.example"), [], "A name that exists but has no A records gives an empty list")


class TestLowestTtl(unittest.TestCase):
    def test_ttl(self):
        self.assertEqual(lowest_ttl(ZONE, "rosiesbakery.example"), 3600)
        self.assertEqual(lowest_ttl(ZONE, "shop.rosiesbakery.example"), 60, "The CNAME has 300 but the A records have 60: use the lowest")
        self.assertEqual(lowest_ttl(ZONE, "www.rosiesbakery.example"), 3600)

    def test_only_a_and_cname_count(self):
        zone = {"x.example": [("MX", "mail.example", 5), ("A", "192.0.2.1", 600)]}
        self.assertEqual(lowest_ttl(zone, "x.example"), 600)


class TestCache(unittest.TestCase):
    def test_hit_and_expire(self):
        cache = DnsCache()
        cache.put("shop.rosiesbakery.example", ["198.51.100.20"], 60, now=1000)
        self.assertEqual(cache.get("shop.rosiesbakery.example", now=1000), ["198.51.100.20"])
        self.assertEqual(cache.get("shop.rosiesbakery.example", now=1059), ["198.51.100.20"])
        self.assertIsNone(cache.get("shop.rosiesbakery.example", now=1060), "After 60 seconds, the answer has expired")

    def test_miss(self):
        self.assertIsNone(DnsCache().get("rosiesbakery.example", now=0))

    def test_replace(self):
        cache = DnsCache()
        cache.put("a.example", ["192.0.2.1"], 10, now=0)
        cache.put("a.example", ["192.0.2.2"], 10, now=5)
        self.assertEqual(cache.get("a.example", now=12), ["192.0.2.2"])


if __name__ == "__main__":
    unittest.main()
