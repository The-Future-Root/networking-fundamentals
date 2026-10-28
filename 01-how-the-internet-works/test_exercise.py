import random
import unittest

from exercise import missing_packets, reassemble, split_message


class TestSplit(unittest.TestCase):
    def test_split(self):
        self.assertEqual(split_message("Your order has shipped!", 8), [(0, "Your ord"), (1, "er has s"), (2, "hipped!")])

    def test_exact_fit(self):
        self.assertEqual(split_message("abcdef", 3), [(0, "abc"), (1, "def")])

    def test_short_and_empty(self):
        self.assertEqual(split_message("hi", 10), [(0, "hi")])
        self.assertEqual(split_message("", 10), [], "An empty message needs no packets")


class TestMissing(unittest.TestCase):
    def test_missing(self):
        self.assertEqual(missing_packets([(0, "a"), (2, "c")], 3), [1])
        self.assertEqual(missing_packets([(3, "d"), (0, "a")], 5), [1, 2, 4])

    def test_none_missing(self):
        self.assertEqual(missing_packets([(1, "b"), (0, "a")], 2), [])


class TestReassemble(unittest.TestCase):
    def test_out_of_order(self):
        packets = [(2, "hipped!"), (0, "Your ord"), (1, "er has s")]
        self.assertEqual(reassemble(packets, 3), "Your order has shipped!")

    def test_duplicates(self):
        packets = [(1, "lo"), (0, "hel"), (1, "lo"), (0, "hel")]
        self.assertEqual(reassemble(packets, 2), "hello", "A packet that arrives twice should only be used once")

    def test_missing_raises(self):
        with self.assertRaises(ValueError):
            reassemble([(0, "Your ord"), (2, "hipped!")], 3)

    def test_round_trip(self):
        rng = random.Random(1)
        message = "".join(rng.choice("abcdefghij ") for _ in range(5000))
        packets = split_message(message, 37)
        shuffled = packets + rng.sample(packets, 40)
        rng.shuffle(shuffled)
        self.assertEqual(reassemble(shuffled, len(packets)), message)


if __name__ == "__main__":
    unittest.main()
