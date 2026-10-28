import http.server
import socket
import threading
import time
import unittest

from exercise import check, check_all, report


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/ok":
            self.reply(200, b"fresh bread")
        elif self.path == "/created":
            self.reply(201, b"")
        elif self.path == "/moved":
            self.send_response(301)
            self.send_header("Location", "/ok")
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif self.path == "/broken":
            self.reply(500, b"oops")
        elif self.path.startswith("/slow"):
            time.sleep(0.4)
            self.reply(200, b"slow")
        elif self.path == "/very-slow":
            time.sleep(1.5)
            self.reply(200, b"too late")
        else:
            self.reply(404, b"no such page")

    def reply(self, status, body):
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class UptimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()


class TestCheck(UptimeTests):
    def test_up(self):
        result = check(self.base + "/ok")
        self.assertEqual(result["url"], self.base + "/ok")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], 200)
        self.assertIsNone(result["error"])
        self.assertIsInstance(result["ms"], float)
        self.assertGreaterEqual(result["ms"], 0)

    def test_other_success(self):
        self.assertEqual(check(self.base + "/created")["status"], 201)
        self.assertTrue(check(self.base + "/created")["ok"])

    def test_redirect_followed(self):
        result = check(self.base + "/moved")
        self.assertEqual(result["status"], 200, "urllib follows redirects, so you get the final page's status")
        self.assertTrue(result["ok"])

    def test_not_found(self):
        result = check(self.base + "/missing")
        self.assertEqual((result["ok"], result["status"], result["error"]), (False, 404, None),
                         "A 404 is a real answer from the server: ok is False, status is 404, and there's no error")

    def test_server_error(self):
        result = check(self.base + "/broken")
        self.assertEqual((result["ok"], result["status"]), (False, 500))

    def test_nothing_listening(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        result = check(f"http://127.0.0.1:{port}/")
        self.assertFalse(result["ok"])
        self.assertIsNone(result["status"], "No server answered, so there's no status")
        self.assertIn("refused", result["error"].lower())

    def test_timeout(self):
        start = time.perf_counter()
        result = check(self.base + "/very-slow", timeout=0.3)
        self.assertLess(time.perf_counter() - start, 1.2, "Pass the timeout to urlopen")
        self.assertFalse(result["ok"])
        self.assertIsNone(result["status"])
        self.assertEqual(result["error"], "timed out")

    def test_timing(self):
        result = check(self.base + "/slow")
        self.assertGreaterEqual(result["ms"], 390, "ms should be how long the whole request took, in milliseconds")
        self.assertEqual(result["ms"], round(result["ms"], 1))


class TestCheckAll(UptimeTests):
    def test_order(self):
        urls = [self.base + "/missing", self.base + "/ok", self.base + "/broken"]
        self.assertEqual([r["status"] for r in check_all(urls)], [404, 200, 500], "Results come back in the same order as the URLs")

    def test_at_the_same_time(self):
        urls = [f"{self.base}/slow{i}" for i in range(6)]
        start = time.perf_counter()
        results = check_all(urls, workers=6)
        seconds = time.perf_counter() - start
        self.assertTrue(all(r["ok"] for r in results))
        self.assertLess(seconds, 1.5, "Six 0.4-second checks should run at the same time, not one after another (2.4 seconds)")


class TestReport(unittest.TestCase):
    def test_lines(self):
        results = [
            {"url": "https://example.com", "ok": True, "status": 200, "ms": 84.2, "error": None},
            {"url": "https://example.com/no-such-page", "ok": False, "status": 404, "ms": 91.0, "error": None},
            {"url": "http://127.0.0.1:9", "ok": False, "status": None, "ms": 0.4, "error": "Connection refused"},
        ]
        self.assertEqual(report(results).splitlines(), [
            "UP    200     84.2 ms  https://example.com",
            "DOWN  404     91.0 ms  https://example.com/no-such-page",
            "DOWN  -        0.4 ms  http://127.0.0.1:9  (Connection refused)",
        ])


if __name__ == "__main__":
    unittest.main()
