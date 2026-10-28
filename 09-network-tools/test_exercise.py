import pathlib
import unittest

from exercise import listening_ports, parse_dig, parse_ping

SAMPLES = pathlib.Path(__file__).resolve().parent / "samples"


def sample(name):
    return (SAMPLES / name).read_text()


PARTLY_LOST = """PING 198.51.100.7 (198.51.100.7) 56(84) bytes of data.
64 bytes from 198.51.100.7: icmp_seq=1 ttl=57 time=31.2 ms
64 bytes from 198.51.100.7: icmp_seq=3 ttl=57 time=29.8 ms

--- 198.51.100.7 ping statistics ---
3 packets transmitted, 2 received, 33.3333% packet loss, time 2003ms
rtt min/avg/max/mdev = 29.812/30.506/31.200/0.694 ms
"""

DIG_MX = """
;; ANSWER SECTION:
rosiesbakery.example.	3600	IN	MX	10 mail.rosiesbakery.example.
rosiesbakery.example.	3600	IN	MX	20 backup-mail.rosiesbakery.example.

;; Query time: 31 msec
"""

SS_MIXED = """State  Recv-Q Send-Q Local Address:Port  Peer Address:Port
LISTEN 0      4096       0.0.0.0:22          0.0.0.0:*
LISTEN 0      511      127.0.0.1:8080        0.0.0.0:*
LISTEN 0      4096          [::]:22             [::]:*
LISTEN 0      511          [::1]:8080           [::]:*
LISTEN 0      4096             *:443               *:*
"""


class TestPing(unittest.TestCase):
    def test_all_replies(self):
        self.assertEqual(parse_ping(sample("ping-example.com.txt")),
                         {"sent": 4, "received": 4, "loss_percent": 0.0, "min_ms": 4.98, "avg_ms": 8.055, "max_ms": 9.596})

    def test_no_replies(self):
        self.assertEqual(parse_ping(sample("ping-no-reply.txt")),
                         {"sent": 3, "received": 0, "loss_percent": 100.0, "min_ms": None, "avg_ms": None, "max_ms": None},
                         "With no replies there's no rtt line, so the times are None")

    def test_some_lost(self):
        result = parse_ping(PARTLY_LOST)
        self.assertEqual((result["sent"], result["received"]), (3, 2))
        self.assertAlmostEqual(result["loss_percent"], 33.3333)
        self.assertEqual(result["avg_ms"], 30.506)


class TestDig(unittest.TestCase):
    def test_full_output(self):
        self.assertEqual(parse_dig(sample("dig-example.com.txt")),
                         [("example.com", 52, "A", "172.66.147.243"), ("example.com", 52, "A", "104.20.23.154")])

    def test_short_output(self):
        self.assertEqual(parse_dig(sample("dig-www.github.com.txt")),
                         [("www.github.com", 3600, "CNAME", "github.com"), ("github.com", 60, "A", "20.207.73.82")])

    def test_mx(self):
        self.assertEqual(parse_dig(DIG_MX), [("rosiesbakery.example", 3600, "MX", "10 mail.rosiesbakery.example"),
                                             ("rosiesbakery.example", 3600, "MX", "20 backup-mail.rosiesbakery.example")],
                         "An MX value has a priority and a name: keep both")

    def test_no_answers(self):
        self.assertEqual(parse_dig(";; Got answer:\n;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 1\n\n;; Query time: 20 msec\n"), [])


class TestSs(unittest.TestCase):
    def test_sample(self):
        self.assertEqual(listening_ports(sample("ss-listening.txt")), [5432, 8000, 8901])

    def test_ipv6_and_duplicates(self):
        self.assertEqual(listening_ports(SS_MIXED), [22, 443, 8080], "IPv6 addresses contain colons too: take the part after the last one")

    def test_header_only(self):
        self.assertEqual(listening_ports("State  Recv-Q Send-Q Local Address:Port Peer Address:Port\n"), [])


if __name__ == "__main__":
    unittest.main()
