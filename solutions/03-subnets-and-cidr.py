# Solution to lesson 3: subnets and CIDR


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


def mask_int(prefix):
    """Return the subnet mask for a prefix length, as a 32-bit number: /24 gives 0xFFFFFF00."""
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF


def prefix_to_mask(prefix):
    """Turn a prefix length into a dotted mask: 24 gives '255.255.255.0'."""
    return from_int(mask_int(prefix))


def mask_to_prefix(mask):
    """Turn a dotted mask into a prefix length: '255.255.255.0' gives 24."""
    return bin(to_int(mask)).count("1")


def network_address(cidr):
    """The first address of the network: '192.168.1.130/25' gives '192.168.1.128'."""
    address, prefix = cidr.split("/")
    return from_int(to_int(address) & mask_int(int(prefix)))


def broadcast_address(cidr):
    """The last address of the network: '192.168.1.130/25' gives '192.168.1.255'."""
    address, prefix = cidr.split("/")
    host_bits = 0xFFFFFFFF ^ mask_int(int(prefix))
    return from_int(to_int(address) | host_bits)


def usable_hosts(prefix):
    """How many devices a network of this size can hold. The network and broadcast addresses don't count,
    except that a /31 has 2 (a point-to-point link) and a /32 has 1."""
    if prefix == 32:
        return 1
    if prefix == 31:
        return 2
    return 2 ** (32 - prefix) - 2


def same_network(first, second, prefix):
    """True if the two addresses are in the same network of this prefix length."""
    mask = mask_int(prefix)
    return to_int(first) & mask == to_int(second) & mask


if __name__ == "__main__":
    print(prefix_to_mask(24), prefix_to_mask(20), mask_to_prefix("255.255.252.0"))
    print(network_address("192.168.1.130/25"), broadcast_address("192.168.1.130/25"))
    print(usable_hosts(24), usable_hosts(26), usable_hosts(30))
    print(same_network("10.0.4.20", "10.0.7.200", 22), same_network("10.0.4.20", "10.0.8.1", 22))
