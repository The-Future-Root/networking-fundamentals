# Solution to lesson 4: a tiny DNS resolver

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
    for _ in range(MAX_HOPS):
        if name not in zone:
            raise LookupError(f"{name}: no such name (NXDOMAIN)")
        aliases = records(zone, name, "CNAME")
        if aliases:
            name = aliases[0]
            continue
        return records(zone, name, "A")
    raise ValueError("Too many CNAME hops: is there a loop?")


class DnsCache:
    """Remembers answers until their time to live (TTL) runs out. Times are in seconds."""

    def __init__(self):
        """Start with an empty cache."""
        self._entries = {}

    def put(self, name, addresses, ttl, now):
        """Remember the addresses for name, for ttl seconds from now."""
        self._entries[name] = (addresses, now + ttl)

    def get(self, name, now):
        """Return the remembered addresses, or None if there are none or they've expired."""
        if name not in self._entries:
            return None
        addresses, expires = self._entries[name]
        if now >= expires:
            del self._entries[name]
            return None
        return addresses


def lowest_ttl(zone, name):
    """The TTL to cache an answer for: the lowest TTL of every record used to answer it, following CNAMEs."""
    lowest = None
    for _ in range(MAX_HOPS):
        found = zone[name]
        for kind, value, ttl in found:
            if kind in ("A", "CNAME") and (lowest is None or ttl < lowest):
                lowest = ttl
        aliases = records(zone, name, "CNAME")
        if not aliases:
            return lowest
        name = aliases[0]
    raise ValueError("Too many CNAME hops: is there a loop?")


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
