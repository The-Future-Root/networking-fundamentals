# Lesson 10: a website uptime checker
#
# load_urls is written for you. The tests only use a test server on 127.0.0.1.
# Running this file checks the real websites in sites.txt.
# Test with:  python3 -m unittest -v

import socket
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def load_urls(path):
    """Read a file of URLs, one per line, skipping blank lines and lines starting with #."""
    urls = []
    with open(path) as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def check(url, timeout=5.0):
    """Request url and report what happened. Return a dict with:
    url, ok (True for a 2xx or 3xx status), status (the HTTP status, or None if there was no response),
    ms (how long it took, rounded to 1 decimal place) and error (None, or a short description)."""
    pass


def check_all(urls, timeout=5.0, workers=8):
    """Check every URL at the same time, using a pool of threads. Return the results in the same order as urls."""
    pass


def report(results):
    """Format results as lines like 'UP    200    84.2 ms  https://example.com', one per result."""
    pass


if __name__ == "__main__":
    results = check_all(load_urls("sites.txt"))
    print(report(results))
    up = sum(1 for result in results if result["ok"])
    print(f"{up} of {len(results)} up")
