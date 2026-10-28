import random
import unittest

from exercise import Receiver, segments


class TestInOrder(unittest.TestCase):
    def test_in_order(self):
        receiver = Receiver()
        self.assertEqual(receiver.receive(0, "GET /"), 5)
        self.assertEqual(receiver.receive(5, "menu "), 10)
        self.assertEqual(receiver.delivered, "GET /menu ")


class TestOutOfOrder(unittest.TestCase):
    def test_gap_then_fill(self):
        receiver = Receiver()
        receiver.receive(0, "GET /")
        self.assertEqual(receiver.receive(10, "HTTP/"), 5, "A segment after a gap can't be delivered yet: keep asking for byte 5")
        self.assertEqual(receiver.delivered, "GET /")
        self.assertEqual(receiver.waiting(), 1)
        self.assertEqual(receiver.receive(5, "menu "), 15, "Filling the gap delivers the waiting segment too")
        self.assertEqual(receiver.delivered, "GET /menu HTTP/")
        self.assertEqual(receiver.waiting(), 0)

    def test_first_segment_late(self):
        receiver = Receiver()
        self.assertEqual(receiver.receive(3, "def"), 0)
        self.assertEqual(receiver.receive(6, "ghi"), 0)
        self.assertEqual(receiver.receive(0, "abc"), 9)
        self.assertEqual(receiver.delivered, "abcdefghi")


class TestDuplicates(unittest.TestCase):
    def test_duplicate_ignored(self):
        receiver = Receiver()
        receiver.receive(0, "GET /")
        self.assertEqual(receiver.receive(0, "GET /"), 5, "A repeat of data already delivered changes nothing")
        self.assertEqual(receiver.delivered, "GET /")
        self.assertEqual(receiver.waiting(), 0, "Don't keep old duplicates waiting")

    def test_overlap(self):
        receiver = Receiver()
        receiver.receive(0, "abcd")
        self.assertEqual(receiver.receive(2, "cdef"), 6, "Only the new part of an overlapping segment is delivered")
        self.assertEqual(receiver.delivered, "abcdef")


class TestRandom(unittest.TestCase):
    def test_shuffled_with_retransmissions(self):
        rng = random.Random(5)
        for trial in range(200):
            message = "".join(rng.choice("abcdefgh") for _ in range(rng.randint(1, 120)))
            parts = segments(message, rng.randint(1, 9))
            arriving = parts + [rng.choice(parts) for _ in range(rng.randint(0, 10))]
            rng.shuffle(arriving)
            receiver = Receiver()
            last_ack = 0
            for seq, data in arriving:
                ack = receiver.receive(seq, data)
                self.assertGreaterEqual(ack, last_ack, "An ACK never goes backwards")
                self.assertEqual(ack, len(receiver.delivered), "The ACK is the number of the next byte expected")
                self.assertTrue(message.startswith(receiver.delivered), "Only ever deliver bytes in order")
                last_ack = ack
            self.assertEqual(receiver.delivered, message)
            self.assertEqual(receiver.waiting(), 0)


if __name__ == "__main__":
    unittest.main()
