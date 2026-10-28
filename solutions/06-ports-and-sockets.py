# Solution to lesson 6: talking over sockets

import socket
import threading


def handle_client(connection):
    """Serve one client of the shout server: read until the client stops sending, reply with the text in capitals, then close."""
    with connection:
        data = b""
        while True:
            chunk = connection.recv(1024)
            if not chunk:
                break
            data += chunk
        connection.sendall(data.decode("utf-8").upper().encode("utf-8"))


def tcp_request(host, port, text, timeout=2.0):
    """Connect over TCP, send text, say we've finished sending, and return everything the server sends back, as text."""
    with socket.create_connection((host, port), timeout=timeout) as connection:
        connection.sendall(text.encode("utf-8"))
        connection.shutdown(socket.SHUT_WR)
        reply = b""
        while True:
            chunk = connection.recv(1024)
            if not chunk:
                break
            reply += chunk
    return reply.decode("utf-8")


def udp_request(host, port, text, timeout=1.0):
    """Send text in one UDP datagram and return the reply as text, or None if no reply arrives in time."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(text.encode("utf-8"), (host, port))
        try:
            data, _ = sock.recvfrom(65535)
        except (socket.timeout, ConnectionError):
            return None
    return data.decode("utf-8")


def is_port_open(host, port, timeout=1.0):
    """Return True if something is listening for TCP connections on this port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def start_shout_server(host="127.0.0.1", port=0):
    """Start the shout server in the background. Return the port it's listening on."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()

    def serve():
        while True:
            connection, _ = server.accept()
            threading.Thread(target=handle_client, args=(connection,), daemon=True).start()

    threading.Thread(target=serve, daemon=True).start()
    return server.getsockname()[1]


if __name__ == "__main__":
    port = start_shout_server()
    print("Shout server listening on port", port)
    print(tcp_request("127.0.0.1", port, "is the bakery open on sunday?"))
    print("port", port, "open:", is_port_open("127.0.0.1", port))
    with socket.socket() as spare:
        spare.bind(("127.0.0.1", 0))
        unused = spare.getsockname()[1]
    print("port", unused, "open:", is_port_open("127.0.0.1", unused))
    print(udp_request("127.0.0.1", unused, "hello?", timeout=0.5))
