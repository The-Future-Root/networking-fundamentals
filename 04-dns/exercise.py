# Lesson 4: a tiny DNS resolver
#
# ZONE, records() and DnsCache.__init__ are written for you.
# Test with:  python3 -m unittest -v

# A zone: what an authoritative DNS server knows. Each name has a list of (type, value, ttl) records.
ZONE = {
    "rosiesbakery.example": [("A", "203.0.113.10", 3600), ("MX", "mail.rosiesbakery.example", 3600)],
    "www.rosiesbakery.example": [("CNAME", "rosiesbakery.example", 3600)],
    "shop.rosiesbakery.example": [("CNAME", "shops.payhost.example", 300)],
    "shops.payhost.example": [("A", "198.51.100.20", 60), ("A", "198.51.100.21", 60)],
    "mail.rosiesbakery.example": [("A", "203.0.113.25", 3600)],
    "loop-a.example": [("CNAME", "loop-b.example", 60)],
    "loop-b.example": [("CNAME", "loop-a.example", 60)],
}

MAX_HOPS = 8


def records(zone, name, record_type):
    """Return the values of every record of this type for this name, in the order they're listed."""
    values = []
    for kind, value, _ in zone.get(name, []):
        if kind == record_type:
            values.append(value)
    return values


def resolve(zone, name):
    """Return the list of IPv4 addresses for name, following CNAME records.
    Raise LookupError if the name doesn't exist, and ValueError if CNAMEs go round more than MAX_HOPS times."""
    pass


class DnsCache:
    """Remembers answers until their time to live (TTL) runs out. Times are in seconds."""

    def __init__(self):
        """Start with an empty cache."""
        self._entries = {}

    def put(self, name, addresses, ttl, now):
        """Remember the addresses for name, for ttl seconds from now."""
        pass

    def get(self, name, now):
        """Return the remembered addresses, or None if there are none or they've expired."""
        pass


def lowest_ttl(zone, name):
    """The TTL to cache an answer for: the lowest TTL of every record used to answer it, following CNAMEs."""
    pass


if __name__ == "__main__":
    print(resolve(ZONE, "www.rosiesbakery.example"))
    print(resolve(ZONE, "shop.rosiesbakery.example"), lowest_ttl(ZONE, "shop.rosiesbakery.example"))
    print(records(ZONE, "rosiesbakery.example", "MX"))
    cache = DnsCache()
    cache.put("shop.rosiesbakery.example", ["198.51.100.20", "198.51.100.21"], 60, now=1000)
    print(cache.get("shop.rosiesbakery.example", now=1030), cache.get("shop.rosiesbakery.example", now=1060))
    try:
        resolve(ZONE, "nope.rosiesbakery.example")
    except LookupError as error:
        print(error)
