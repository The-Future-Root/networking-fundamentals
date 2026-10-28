# Networking Fundamentals

What actually happens when you type a web address and press Enter? In about a tenth of a second, your computer finds out where the site lives, opens a connection across dozens of networks, agrees on encryption, asks for the page, and gets it back in pieces that it puts in order. This course explains each of those steps, and has you write small Python programs for each one, so the ideas stick.

You'll learn how IP addresses and subnets work, what DNS does, how TCP makes an unreliable network reliable, what an HTTP request really looks like, how HTTPS keeps it private, and how to use the standard tools for finding out what's wrong when a connection fails.

## Who this is for

Anyone who uses the internet and wants to understand it: new developers, people starting in IT support or security, and the curious. The exercises are in Python, so you should know the basics: functions, loops, lists, dictionaries and strings. If you need a refresher, see [Python Basics](https://github.com/The-Future-Root/python-basics).

## What you need

- **Python 3.10 or newer**, from [python.org](https://www.python.org/downloads/). Check with `python3 --version` (on Windows, `python --version`).
- **A text editor**, such as VS Code.
- A terminal, to try the commands. They're shown as they run on Linux. Most are the same on macOS, and Windows has its own versions, mentioned in lesson 9.

The exercises don't need an internet connection: anything that uses the network only talks to `127.0.0.1`, your own computer. The "try it" commands in the lessons do use the internet, but only to look at public sites like `example.com`, a domain set aside for examples.

## Lessons

| # | Lesson | You'll learn | Exercise |
|---|---|---|---|
| 1 | [How the internet works](./01-how-the-internet-works/) | Packets, routers, and the layers of networking | Split a message into packets and put it back together |
| 2 | [IP addresses](./02-ip-addresses/) | IPv4, binary, private and public addresses, NAT and IPv6 | Validate and classify addresses |
| 3 | [Subnets and CIDR](./03-subnets-and-cidr/) | Network masks, `/24`, and how a computer decides what's local | Subnet calculator |
| 4 | [DNS](./04-dns/) | How names become addresses, record types and caching | A tiny DNS resolver |
| 5 | [TCP and UDP](./05-tcp-and-udp/) | Reliable streams versus fast datagrams | Put out-of-order TCP data back together |
| 6 | [Ports and sockets](./06-ports-and-sockets/) | Ports, and writing real network programs | A TCP server and client |
| 7 | [HTTP](./07-http/) | Requests, responses, methods, headers and status codes | Read and write HTTP messages |
| 8 | [HTTPS and TLS](./08-https-and-tls/) | Encryption, certificates and how trust works | Check a certificate like a browser does |
| 9 | [Network tools](./09-network-tools/) | `ping`, `traceroute`, `dig`, `curl` and `ss` | Read the tools' output with Python |
| 10 | [Project: uptime checker](./10-project-uptime-checker/) | Putting it together | A tool that checks whether websites are up |

## How the exercises work

Each lesson folder has `exercise.py`, where you write your code, and `test_exercise.py`, which checks it. Run the tests from the lesson's folder:

```bash
cd 02-ip-addresses
python3 -m unittest -v
```

On Windows, type `python` instead of `python3`. Hints are at the end of each lesson, and full solutions are in [solutions/](./solutions/).

## About the examples

Example addresses come from the ranges set aside for documentation (`192.0.2.x`, `198.51.100.x`, `203.0.113.x`), and example names end in `.example`, so none of them belong to anyone. Real outputs from real tools, like `ping example.com`, are shown exactly as they came out, except where noted.

## About the diagrams

The colours keep the same meaning throughout: **blue** for your device and data, **purple** for other machines on the network, **amber** for the step happening now, **green** for success or the answer, and **red** for failure or loss.

## License

The code in this repository is released under the [MIT License](./LICENSE). The lesson text and diagrams are released under [Creative Commons Attribution 4.0](./LICENSE-CONTENT) (CC BY 4.0): you may share and adapt them, including for your own teaching, as long as you credit The Future Root.
