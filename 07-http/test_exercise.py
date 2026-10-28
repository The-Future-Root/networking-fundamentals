import http.client
import socket
import threading
import unittest
import urllib.error
import urllib.request

from exercise import build_response, parse_headers, parse_request, parse_response, status_class

REQUEST = ("POST /orders?express=yes HTTP/1.1\r\n"
           "Host: rosiesbakery.example\r\n"
           "Content-Type: application/json\r\n"
           "Content-Length: 27\r\n"
           "\r\n"
           '{"item": "scone", "qty": 2}')


def serve_once(raw_response):
    """Start a server that answers one connection with raw_response, and remembers the request it got."""
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen()
    seen = {}

    def run():
        connection, _ = server.accept()
        with connection:
            data = b""
            while b"\r\n\r\n" not in data:
                data += connection.recv(4096)
            seen["request"] = data.decode()
            connection.sendall(raw_response.encode("utf-8"))
        server.close()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return server.getsockname()[1], seen, thread


class TestHeaders(unittest.TestCase):
    def test_parse_headers(self):
        self.assertEqual(parse_headers(["Content-Type: text/html", "X-Cache:HIT"]), {"content-type": "text/html", "x-cache": "HIT"})

    def test_colon_in_value(self):
        self.assertEqual(parse_headers(["Host: localhost:8080"]), {"host": "localhost:8080"}, "Split at the first colon only")


class TestParseRequest(unittest.TestCase):
    def test_request(self):
        request = parse_request(REQUEST)
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/orders")
        self.assertEqual(request["query"], "express=yes")
        self.assertEqual(request["version"], "HTTP/1.1")
        self.assertEqual(request["headers"]["content-type"], "application/json", "Header names are lower case in the dict")
        self.assertEqual(request["headers"]["host"], "rosiesbakery.example")
        self.assertEqual(request["body"], '{"item": "scone", "qty": 2}')

    def test_no_query(self):
        request = parse_request("GET / HTTP/1.1\r\nHost: rosiesbakery.example\r\n\r\n")
        self.assertEqual((request["path"], request["query"], request["body"]), ("/", "", ""))

    def test_real_client_request(self):
        port, seen, thread = serve_once(build_response(200, "ok"))
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        connection.request("GET", "/menu?day=sunday", headers={"Accept": "text/plain"})
        connection.getresponse().read()
        connection.close()
        thread.join(2)
        request = parse_request(seen["request"])
        self.assertEqual((request["method"], request["path"], request["query"]), ("GET", "/menu", "day=sunday"))
        self.assertEqual(request["headers"]["host"], f"127.0.0.1:{port}")
        self.assertEqual(request["headers"]["accept"], "text/plain")


class TestParseResponse(unittest.TestCase):
    def test_response(self):
        raw = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 9\r\n\r\nNo scones"
        response = parse_response(raw)
        self.assertEqual(response["status"], 404, "The status should be a number")
        self.assertEqual(response["reason"], "Not Found", "The reason can contain spaces")
        self.assertEqual(response["headers"]["content-length"], "9")
        self.assertEqual(response["body"], "No scones")


class TestBuildResponse(unittest.TestCase):
    def test_format(self):
        self.assertEqual(build_response(200, "Open 9 to 4 on Sundays."),
                         "HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 23\r\n\r\nOpen 9 to 4 on Sundays.")

    def test_reason_phrases(self):
        self.assertTrue(build_response(404).startswith("HTTP/1.1 404 Not Found\r\n"))
        self.assertTrue(build_response(301).startswith("HTTP/1.1 301 Moved Permanently\r\n"))
        self.assertIn("Content-Length: 0\r\n", build_response(204))

    def test_length_counts_bytes(self):
        self.assertIn("Content-Length: 5\r\n", build_response(200, "café"), "Content-Length counts bytes, not characters: é is 2 bytes in UTF-8")

    def test_content_type(self):
        self.assertIn("Content-Type: text/html\r\n", build_response(200, "<p>hi</p>", "text/html"))

    def test_real_client_understands_it(self):
        port, _, thread = serve_once(build_response(200, "Fresh bread daily", "text/plain"))
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as reply:
            self.assertEqual(reply.status, 200)
            self.assertEqual(reply.read().decode(), "Fresh bread daily", "A real HTTP client should be able to read your response")
        thread.join(2)

    def test_real_client_sees_error(self):
        port, _, thread = serve_once(build_response(404, "No such page"))
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/missing", timeout=2)
        self.assertEqual(caught.exception.code, 404)
        thread.join(2)


class TestStatusClass(unittest.TestCase):
    def test_classes(self):
        self.assertEqual(status_class(200), "success")
        self.assertEqual(status_class(201), "success")
        self.assertEqual(status_class(301), "redirect")
        self.assertEqual(status_class(404), "client error")
        self.assertEqual(status_class(503), "server error")
        self.assertEqual(status_class(101), "informational")


if __name__ == "__main__":
    unittest.main()
