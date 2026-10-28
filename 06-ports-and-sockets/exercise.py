# Lesson 6: talking over sockets
#
# start_shout_server is written for you. Everything here only talks to 127.0.0.1, your own computer.
# Test with:  python3 -m unittest -v

import socket
import threading


def handle_client(connection):
    """Serve one client of the shout server: read until the client stops sending, reply with the text in capitals, then close."""
    pass


def tcp_request(host, port, text, timeout=2.0):
    """Connect over TCP, send text, say we've finished sending, and return everything the server sends back, as text."""
    pass


def udp_request(host, port, text, timeout=1.0):
    """Send text in one UDP datagram and return the reply as text, or None if no reply arrives in time."""
    pass


def is_port_open(host, port, timeout=1.0):
    """Return True if something is listening for TCP connections on this port."""
    pass


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
