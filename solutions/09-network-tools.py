# Solution to lesson 9: reading the output of network tools

import pathlib
import re

SAMPLES = pathlib.Path("samples")   # run this from the lesson folder


def parse_ping(text):
    """Read the summary at the end of Linux ping output. Return a dict with sent, received and loss_percent,
    plus min_ms, avg_ms and max_ms (None if no replies came back)."""
    counts = re.search(r"(\d+) packets transmitted, (\d+) received, ([\d.]+)% packet loss", text)
    result = {"sent": int(counts.group(1)), "received": int(counts.group(2)), "loss_percent": float(counts.group(3)),
              "min_ms": None, "avg_ms": None, "max_ms": None}
    times = re.search(r"= ([\d.]+)/([\d.]+)/([\d.]+)/", text)
    if times:
        result["min_ms"] = float(times.group(1))
        result["avg_ms"] = float(times.group(2))
        result["max_ms"] = float(times.group(3))
    return result


def parse_dig(text):
    """Return the answer records in dig output as (name, ttl, type, value) tuples, with the final dots removed.
    Works on full output (reads the ANSWER SECTION) and on +noall +answer output (every line is an answer)."""
    lines = text.splitlines()
    if ";; ANSWER SECTION:" in lines:
        start = lines.index(";; ANSWER SECTION:") + 1
        lines = lines[start:]
    answers = []
    for line in lines:
        if not line.strip():
            if answers:
                break
            continue
        if line.startswith(";"):
            continue
        name, ttl, _, kind, value = line.split(None, 4)
        answers.append((name.rstrip("."), int(ttl), kind, value.rstrip(".")))
    return answers


def listening_ports(text):
    """Return a sorted list of the port numbers in `ss -tln` output, each once."""
    ports = set()
    for line in text.splitlines()[1:]:
        columns = line.split()
        if len(columns) >= 4:
            ports.add(int(columns[3].rsplit(":", 1)[1]))
    return sorted(ports)


if __name__ == "__main__":
    print(parse_ping((SAMPLES / "ping-example.com.txt").read_text()))
    print(parse_ping((SAMPLES / "ping-no-reply.txt").read_text()))
    print(parse_dig((SAMPLES / "dig-example.com.txt").read_text()))
    print(parse_dig((SAMPLES / "dig-www.github.com.txt").read_text()))
    print(listening_ports((SAMPLES / "ss-listening.txt").read_text()))
