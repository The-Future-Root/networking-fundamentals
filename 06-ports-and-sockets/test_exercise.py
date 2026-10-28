import socket
import threading
import unittest

from exercise import handle_client, is_port_open, start_shout_server, tcp_request, udp_request

HOST = "127.0.0.1"


def unused_port():
    with socket.socket() as sock:
        sock.bind((HOST, 0))
        return sock.getsockname()[1]


def reference_tcp_server(reply_with):
    """A test server that reads everything, then sends back reply_with(data)."""
    server = socket.socket()
    server.bind((HOST, 0))
    server.listen()

    def serve():
        while True:
            connection, _ = server.accept()
            with connection:
                data = b""
                while True:
                    chunk = connection.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                connection.sendall(reply_with(data))

    threading.Thread(target=serve, daemon=True).start()
    return server.getsockname()[1]


def reference_udp_server():
    """A test server that answers every datagram with 'got: ' and what it received."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, 0))

    def serve():
        while True:
            data, address = sock.recvfrom(65535)
            sock.sendto(b"got: " + data, address)

    threading.Thread(target=serve, daemon=True).start()
    return sock.getsockname()[1]


class TestHandleClient(unittest.TestCase):
    def test_shouts_back(self):
        server_side, client_side = socket.socketpair()
        with client_side:
            client_side.sendall(b"is the bakery open on sunday?")
            client_side.shutdown(socket.SHUT_WR)
            thread = threading.Thread(target=handle_client, args=(server_side,))
            thread.start()
            client_side.settimeout(2)
            reply = b""
            while True:
                chunk = client_side.recv(1024)
                if not chunk:
                    break
                reply += chunk
            thread.join(2)
        self.assertEqual(reply, b"IS THE BAKERY OPEN ON SUNDAY?", "Read until the client stops sending (recv returns b''), reply in capitals, then close")

    def test_long_message(self):
        server_side, client_side = socket.socketpair()
        message = ("croissant " * 20_000).encode()
        sender = threading.Thread(target=lambda: (client_side.sendall(message), client_side.shutdown(socket.SHUT_WR)))
        sender.start()
        worker = threading.Thread(target=handle_client, args=(server_side,))
        worker.start()
        client_side.settimeout(5)
        reply = b""
        while True:
            chunk = client_side.recv(65536)
            if not chunk:
                break
            reply += chunk
        client_side.close()
        self.assertEqual(reply, message.upper(), "One recv() can return part of the data: keep reading until it returns b''")


class TestTcpRequest(unittest.TestCase):
    def test_round_trip(self):
        port = reference_tcp_server(lambda data: b"you said: " + data)
        self.assertEqual(tcp_request(HOST, port, "hello"), "you said: hello")

    def test_long_reply(self):
        port = reference_tcp_server(lambda data: data * 50_000)
        self.assertEqual(tcp_request(HOST, port, "ab"), "ab" * 50_000, "Keep reading until the server closes the connection")

    def test_unicode(self):
        port = reference_tcp_server(lambda data: data)
        self.assertEqual(tcp_request(HOST, port, "café crème"), "café crème", "Encode and decode with UTF-8")

    def test_with_shout_server(self):
        port = start_shout_server()
        self.assertEqual(tcp_request(HOST, port, "two scones please"), "TWO SCONES PLEASE")

    def test_nothing_listening(self):
        with self.assertRaises(ConnectionRefusedError):
            tcp_request(HOST, unused_port(), "hello")


class TestUdpRequest(unittest.TestCase):
    def test_reply(self):
        port = reference_udp_server()
        self.assertEqual(udp_request(HOST, port, "ping"), "got: ping")

    def test_no_reply(self):
        self.assertIsNone(udp_request(HOST, unused_port(), "anyone there?", timeout=0.3), "With no reply in time, return None")


class TestIsPortOpen(unittest.TestCase):
    def test_open(self):
        port = reference_tcp_server(lambda data: b"")
        self.assertTrue(is_port_open(HOST, port))

    def test_closed(self):
        self.assertFalse(is_port_open(HOST, unused_port()))


if __name__ == "__main__":
    unittest.main()
