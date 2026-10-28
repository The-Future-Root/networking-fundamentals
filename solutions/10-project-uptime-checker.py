# Solution to lesson 10: a website uptime checker

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
    start = time.perf_counter()
    status = None
    error = None
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            status = response.status
    except urllib.error.HTTPError as problem:
        status = problem.code
    except urllib.error.URLError as problem:
        reason = problem.reason
        error = "timed out" if isinstance(reason, (socket.timeout, TimeoutError)) else str(reason)
    except (socket.timeout, TimeoutError):
        error = "timed out"
    ms = round((time.perf_counter() - start) * 1000, 1)
    ok = status is not None and 200 <= status < 400
    return {"url": url, "ok": ok, "status": status, "ms": ms, "error": error}


def check_all(urls, timeout=5.0, workers=8):
    """Check every URL at the same time, using a pool of threads. Return the results in the same order as urls."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda url: check(url, timeout), urls))


def report(results):
    """Format results as lines like 'UP    200    84.2 ms  https://example.com', one per result."""
    lines = []
    for result in results:
        state = "UP" if result["ok"] else "DOWN"
        status = str(result["status"]) if result["status"] is not None else "-"
        line = f"{state:<5} {status:<4} {result['ms']:>7.1f} ms  {result['url']}"
        if result["error"]:
            line += f"  ({result['error']})"
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    results = check_all(load_urls("sites.txt"))
    print(report(results))
    up = sum(1 for result in results if result["ok"])
    print(f"{up} of {len(results)} up")
