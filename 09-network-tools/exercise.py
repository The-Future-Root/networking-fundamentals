# Lesson 9: reading the output of network tools
#
# The samples folder has real output from ping, dig and ss. Run this file from the lesson folder.
# Test with:  python3 -m unittest -v

import pathlib
import re

SAMPLES = pathlib.Path("samples")   # run this from the lesson folder


def parse_ping(text):
    """Read the summary at the end of Linux ping output. Return a dict with sent, received and loss_percent,
    plus min_ms, avg_ms and max_ms (None if no replies came back)."""
    pass


def parse_dig(text):
    """Return the answer records in dig output as (name, ttl, type, value) tuples, with the final dots removed.
    Works on full output (reads the ANSWER SECTION) and on +noall +answer output (every line is an answer)."""
    pass


def listening_ports(text):
    """Return a sorted list of the port numbers in `ss -tln` output, each once."""
    pass


if __name__ == "__main__":
    print(parse_ping((SAMPLES / "ping-example.com.txt").read_text()))
    print(parse_ping((SAMPLES / "ping-no-reply.txt").read_text()))
    print(parse_dig((SAMPLES / "dig-example.com.txt").read_text()))
    print(parse_dig((SAMPLES / "dig-www.github.com.txt").read_text()))
    print(listening_ports((SAMPLES / "ss-listening.txt").read_text()))
