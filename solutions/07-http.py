# Solution to lesson 7: reading and writing HTTP messages

from http import HTTPStatus


def split_head(message):
    """Split an HTTP message into its head lines and its body, at the first blank line (CRLF CRLF)."""
    head, _, body = message.partition("\r\n\r\n")
    return head.split("\r\n"), body


def parse_headers(lines):
    """Turn header lines like 'Content-Type: text/html' into a dict with lower-case names."""
    headers = {}
    for line in lines:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    return headers


def parse_request(raw):
    """Parse a request. Return a dict with method, path, query, version, headers and body."""
    lines, body = split_head(raw)
    method, target, version = lines[0].split(" ")
    path, _, query = target.partition("?")
    return {"method": method, "path": path, "query": query, "version": version,
            "headers": parse_headers(lines[1:]), "body": body}


def parse_response(raw):
    """Parse a response. Return a dict with version, status (an int), reason, headers and body."""
    lines, body = split_head(raw)
    version, status, reason = lines[0].split(" ", 2)
    return {"version": version, "status": int(status), "reason": reason,
            "headers": parse_headers(lines[1:]), "body": body}


def build_response(status, body="", content_type="text/plain; charset=utf-8"):
    """Build a complete HTTP/1.1 response as text, with Content-Type and Content-Length headers."""
    reason = HTTPStatus(status).phrase
    length = len(body.encode("utf-8"))
    return (f"HTTP/1.1 {status} {reason}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {length}\r\n"
            "\r\n"
            f"{body}")


def status_class(status):
    """Describe a status code: 'informational', 'success', 'redirect', 'client error' or 'server error'."""
    return {1: "informational", 2: "success", 3: "redirect", 4: "client error", 5: "server error"}[status // 100]


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
