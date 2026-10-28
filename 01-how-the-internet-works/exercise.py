# Lesson 1: splitting a message into packets
#
# Test with:  python3 -m unittest -v


def split_message(message, size):
    """Split message into packets of at most `size` characters. Return a list of (number, chunk) pairs, numbered from 0."""
    pass


def missing_packets(packets, total):
    """Return a sorted list of the packet numbers from 0 to total - 1 that haven't arrived."""
    pass


def reassemble(packets, total):
    """Put packets that arrived in any order (possibly with duplicates) back into the message.
    Raise ValueError if any packet is missing."""
    pass


if __name__ == "__main__":
    packets = split_message("Your order has shipped!", 8)
    print(packets)
    arrived = [packets[2], packets[0], packets[1], packets[0]]
    print(reassemble(arrived, len(packets)))
    print(missing_packets([packets[0], packets[2]], 3))
