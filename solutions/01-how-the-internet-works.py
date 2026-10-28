# Solution to lesson 1: splitting a message into packets


def split_message(message, size):
    """Split message into packets of at most `size` characters. Return a list of (number, chunk) pairs, numbered from 0."""
    packets = []
    for start in range(0, len(message), size):
        packets.append((len(packets), message[start:start + size]))
    return packets


def missing_packets(packets, total):
    """Return a sorted list of the packet numbers from 0 to total - 1 that haven't arrived."""
    arrived = set()
    for number, _ in packets:
        arrived.add(number)
    missing = []
    for number in range(total):
        if number not in arrived:
            missing.append(number)
    return missing


def reassemble(packets, total):
    """Put packets that arrived in any order (possibly with duplicates) back into the message.
    Raise ValueError if any packet is missing."""
    missing = missing_packets(packets, total)
    if missing:
        raise ValueError(f"Missing packets: {missing}")
    chunks = {}
    for number, chunk in packets:
        chunks[number] = chunk
    message = ""
    for number in range(total):
        message += chunks[number]
    return message


if __name__ == "__main__":
    packets = split_message("Your order has shipped!", 8)
    print(packets)
    arrived = [packets[2], packets[0], packets[1], packets[0]]
    print(reassemble(arrived, len(packets)))
    print(missing_packets([packets[0], packets[2]], 3))
