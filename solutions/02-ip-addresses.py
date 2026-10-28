# Solution to lesson 2: working with IPv4 addresses


def is_valid_ipv4(text):
    """Return True if text is an IPv4 address: four numbers from 0 to 255, separated by dots, with no leading zeros."""
    parts = text.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or not part.isascii():
            return False
        if len(part) > 1 and part[0] == "0":
            return False
        if int(part) > 255:
            return False
    return True


def to_int(address):
    """Turn an address like '192.168.1.10' into one 32-bit number."""
    number = 0
    for part in address.split("."):
        number = number * 256 + int(part)
    return number


def from_int(number):
    """Turn a 32-bit number back into an address like '192.168.1.10'."""
    parts = []
    for shift in (24, 16, 8, 0):
        parts.append(str((number >> shift) & 255))
    return ".".join(parts)


def to_binary(address):
    """Show an address in binary, 8 digits per part: '11000000.10101000.00000001.00001010'."""
    parts = []
    for part in address.split("."):
        parts.append(format(int(part), "08b"))
    return ".".join(parts)


def address_type(address):
    """Return 'loopback', 'private', 'link-local' or 'public' for an IPv4 address."""
    first, second = [int(part) for part in address.split(".")[:2]]
    if first == 127:
        return "loopback"
    if first == 10:
        return "private"
    if first == 172 and 16 <= second <= 31:
        return "private"
    if first == 192 and second == 168:
        return "private"
    if first == 169 and second == 254:
        return "link-local"
    return "public"


if __name__ == "__main__":
    for text in ["192.168.1.10", "256.1.1.1", "10.0.0.01", "8.8.8.8"]:
        print(text, is_valid_ipv4(text))
    print(to_binary("192.168.1.10"))
    print(to_int("192.168.1.10"), from_int(3232235786))
    for address in ["127.0.0.1", "172.20.5.9", "172.32.0.1", "169.254.10.3", "8.8.8.8"]:
        print(address, address_type(address))
