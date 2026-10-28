# Lesson 7: reading and writing HTTP messages
#
# split_head is written for you.
# Test with:  python3 -m unittest -v

from http import HTTPStatus


def split_head(message):
    """Split an HTTP message into its head lines and its body, at the first blank line (CRLF CRLF)."""
    head, _, body = message.partition("\r\n\r\n")
    return head.split("\r\n"), body


def parse_headers(lines):
    """Turn header lines like 'Content-Type: text/html' into a dict with lower-case names."""
    pass


def parse_request(raw):
    """Parse a request. Return a dict with method, path, query, version, headers and body."""
    pass


def parse_response(raw):
    """Parse a response. Return a dict with version, status (an int), reason, headers and body."""
    pass


def build_response(status, body="", content_type="text/plain; charset=utf-8"):
    """Build a complete HTTP/1.1 response as text, with Content-Type and Content-Length headers."""
    pass


def status_class(status):
    """Describe a status code: 'informational', 'success', 'redirect', 'client error' or 'server error'."""
    pass


if __name__ == "__main__":
    request = ("GET /menu?day=sunday HTTP/1.1\r\n"
               "Host: rosiesbakery.example\r\n"
               "User-Agent: curl/8.11.0\r\n"
               "Accept: */*\r\n"
               "\r\n")
    print(parse_request(request))
    response = build_response(200, "Open 9 to 4 on Sundays.")
    print(response.replace("\r\n", "\\r\\n\n"))
    print(parse_response(response)["status"], status_class(404), status_class(503))
