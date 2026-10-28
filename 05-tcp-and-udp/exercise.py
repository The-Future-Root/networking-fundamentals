# Lesson 5: how TCP puts data back in order
#
# Receiver.__init__, waiting() and segments() are written for you.
# Test with:  python3 -m unittest -v


class Receiver:
    """The receiving side of a TCP connection.

    Segments arrive as (seq, data): seq is the number of the segment's first byte, counting from 0.
    They can arrive out of order, twice, or overlapping. The receiver delivers bytes to the program
    strictly in order, and after every segment replies with an ACK: the number of the next byte it expects."""

    def __init__(self):
        """Nothing received yet: the next byte expected is byte 0."""
        self.next_expected = 0
        self.delivered = ""
        self._waiting = {}

    def receive(self, seq, data):
        """Take in one segment and return the ACK number to send back."""
        pass

    def _deliver_in_order(self):
        """Move every waiting segment that continues the delivered data into `delivered`."""
        pass

    def waiting(self):
        """How many segments are held back, waiting for a gap before them to be filled."""
        return len(self._waiting)


def segments(message, size, start=0):
    """Split message into TCP-style segments of at most `size` bytes: a list of (seq, data)."""
    result = []
    for offset in range(0, len(message), size):
        result.append((start + offset, message[offset:offset + size]))
    return result


if __name__ == "__main__":
    parts = segments("GET /menu HTTP/1.1", 5)
    print(parts)
    receiver = Receiver()
    for seq, data in [parts[0], parts[2], parts[1], parts[1], parts[3]]:
        ack = receiver.receive(seq, data)
        print(f"got seq {seq:2} {data!r:8} -> ACK {ack:2}  delivered so far: {receiver.delivered!r}")
