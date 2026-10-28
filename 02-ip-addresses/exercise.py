# Lesson 2: working with IPv4 addresses
#
# Don't import the ipaddress module: the point is to do it by hand.
# Test with:  python3 -m unittest -v


def is_valid_ipv4(text):
    """Return True if text is an IPv4 address: four numbers from 0 to 255, separated by dots, with no leading zeros."""
    pass


def to_int(address):
    """Turn an address like '192.168.1.10' into one 32-bit number."""
    pass


def from_int(number):
    """Turn a 32-bit number back into an address like '192.168.1.10'."""
    pass


def to_binary(address):
    """Show an address in binary, 8 digits per part: '11000000.10101000.00000001.00001010'."""
    pass


def address_type(address):
    """Return 'loopback', 'private', 'link-local' or 'public' for an IPv4 address."""
    pass


if __name__ == "__main__":
    for text in ["192.168.1.10", "256.1.1.1", "10.0.0.01", "8.8.8.8"]:
        print(text, is_valid_ipv4(text))
    print(to_binary("192.168.1.10"))
    print(to_int("192.168.1.10"), from_int(3232235786))
    for address in ["127.0.0.1", "172.20.5.9", "172.32.0.1", "169.254.10.3", "8.8.8.8"]:
        print(address, address_type(address))
