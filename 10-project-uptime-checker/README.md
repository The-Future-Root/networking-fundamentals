# 10. Project: an uptime checker

Businesses run small programs that check their websites every minute and raise the alarm when one stops answering. In this project you'll build one. It reads a list of URLs, checks them all at once, and prints a report:

```
UP    200    568.7 ms  https://example.com
UP    200    756.2 ms  https://www.python.org
DOWN  404    576.3 ms  https://example.com/no-such-page
DOWN  -      259.4 ms  http://127.0.0.1:9  ([Errno 111] Connection refused)
2 of 4 up
```

That's real output from the finished program. Every check uses something from the course: DNS to find each site (lesson 4), a TCP connection to port 80 or 443 (lessons 5 and 6), TLS for the `https` ones (lesson 8), an HTTP request and its status code (lesson 7), and the difference between "refused", "timed out" and "the server answered with an error" (lesson 9).

## Making HTTP requests from Python

In lesson 6 you wrote raw sockets. For real HTTP, Python's `urllib.request` does the DNS lookup, the connection, TLS, redirects and the HTTP itself:

```python
import urllib.request

with urllib.request.urlopen("https://example.com", timeout=5) as response:
    print(response.status)             # 200
    page = response.read().decode()    # the HTML
```

Things can go wrong in three different ways, and a good checker tells them apart:

| What happened | What `urlopen` does | Example |
|---|---|---|
| The server answered with an error status (4xx or 5xx) | raises `urllib.error.HTTPError`, which has `.code` | a `404` for a missing page, a `503` when the site is overloaded |
| No HTTP answer at all | raises `urllib.error.URLError`, which has `.reason` | DNS failed, the connection was refused, a TLS certificate was invalid |
| No answer in time | raises `TimeoutError` (`socket.timeout` is the same thing), sometimes wrapped in a `URLError` | a server that's hung, or a firewall dropping packets |

An `HTTPError` is still a real answer from the server: there's a status code to report. The other two mean there's no status at all.

Redirects (3xx) are followed automatically, so a `301` from `http://` to `https://` ends up as the final page's status, usually `200`. Always pass a `timeout`: without one, a request to a hung server can wait for minutes.

## Checking many sites at once

Checking 50 sites one after another, at half a second each, takes 25 seconds, and nearly all of it is spent waiting for replies. Waiting for the network is the perfect job for **threads**: while one check waits, others can run. `concurrent.futures.ThreadPoolExecutor` makes this short:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(check, urls))
```

`pool.map` runs `check` for every URL, up to 8 at a time, and gives back the results **in the same order as the URLs**, however long each one took.

## The program

Open [exercise.py](./exercise.py). `load_urls(path)` is written for you: it reads [sites.txt](./sites.txt), skipping blank lines and `#` comments. Write:

| Function | What it does |
|---|---|
| `check(url, timeout=5.0)` | requests the URL and returns a dict: `url`; `ok` (`True` for a 2xx or 3xx status); `status` (the status code, or `None` if there was no HTTP answer); `ms` (how long it took in milliseconds, rounded to 1 place); and `error` (`None`, or a short description, which must be `"timed out"` for a timeout) |
| `check_all(urls, timeout=5.0, workers=8)` | checks every URL at the same time with a thread pool, and returns the results in the same order as `urls` |
| `report(results)` | one line per result, like `UP    200     84.2 ms  https://example.com`, with the error in brackets at the end when there is one |

The `report` format, exactly: `UP` or `DOWN` padded to 5 characters, a space, the status (or `-`) padded to 4, a space, the time right-aligned in 7 characters with 1 decimal place, then ` ms  ` and the URL. In an f-string that's `f"{state:<5} {status:<4} {ms:>7.1f} ms  {url}"`.

Run the tests from the lesson folder:

```bash
cd 10-project-uptime-checker
python3 -m unittest -v
```

The tests start a small web server on `127.0.0.1` with pages that answer `200`, `201`, `301`, `404` and `500`, a slow page, and a page that takes too long. They check that six slow checks run at the same time rather than one after another.

Then run it for real. This checks the sites in `sites.txt`, so it needs the internet:

```bash
python3 exercise.py
```

Your times will be different, and `example.com` might be faster or slower, but the `UP` and `DOWN` column should match the output at the top of this page.

<details>
<summary>Hints</summary>

- `check`: record `time.perf_counter()` before the request. Use `try` with `urlopen(url, timeout=timeout)`, and keep `response.status`. Catch `urllib.error.HTTPError` **first** (it's a kind of `URLError`), and keep its `.code`. Then catch `urllib.error.URLError`: if its `.reason` is a `TimeoutError`, the error is `"timed out"`; otherwise use `str(reason)`. Finally, also catch `TimeoutError` on its own.
- `ms` is `round((end - start) * 1000, 1)`. `ok` is `status is not None and 200 <= status < 400`.
- `check_all`: `pool.map` only passes one argument, so use `lambda url: check(url, timeout)`.
- `report`: the status is `str(result["status"])`, or `"-"` when it's `None`. Join the lines with `"\n"`.

</details>

The full answer is in [solutions/10-project-uptime-checker.py](../solutions/10-project-uptime-checker.py).

## Take it further

- Run the check every minute with a loop and `time.sleep(60)`, and only print when a site changes between UP and DOWN.
- Count a site as DOWN only after two failures in a row, so one lost packet doesn't wake anyone up.
- Warn when a site's TLS certificate expires within 14 days, using your `days_left` from lesson 8 and `getpeercert()`.
- Save each result to a CSV file, and work out each site's uptime percentage for the week.

## What you've learned

That's the whole course. You know how packets cross the internet, how addresses and subnets work, how DNS finds a server, how TCP makes a reliable connection out of unreliable packets, what HTTP and HTTPS actually send, and how to track down a fault one layer at a time. From here, good next steps are learning how to run a web server yourself (Nginx or Caddy), the basics of firewalls, and how cloud networks (VPCs, subnets and load balancers) put all of these pieces together.
