# Solution to lesson 8: checking a website's certificate

import ssl

# The certificate example.com sent on 2026-10-26, as Python's ssl module shows it (getpeercert()).
EXAMPLE_CERT = {
    "subject": ((("commonName", "example.com"),),),
    "issuer": ((("countryName", "US"),), (("organizationName", "SSL Corporation"),), (("commonName", "Cloudflare TLS Issuing ECC CA 3"),)),
    "notBefore": "Sep 26 22:49:11 2026 GMT",
    "notAfter": "Dec 25 22:56:35 2026 GMT",
    "subjectAltName": (("DNS", "example.com"), ("DNS", "*.example.com")),
    "serialNumber": "01EEE6AABB521D5E14FC315FD9985690",
    "version": 3,
}

DAY = 24 * 60 * 60


def dns_names(cert):
    """Return the host names the certificate is for: the DNS entries of its subjectAltName, in order."""
    names = []
    for kind, value in cert.get("subjectAltName", ()):
        if kind == "DNS":
            names.append(value)
    return names


def issuer_name(cert):
    """Return the issuer's commonName: the certificate authority that signed it."""
    for part in cert["issuer"]:
        for key, value in part:
            if key == "commonName":
                return value
    return None


def hostname_matches(pattern, hostname):
    """True if a certificate name like 'example.com' or '*.example.com' covers this host name.
    Case doesn't matter. A '*' must be the whole first label, and stands for exactly one label."""
    pattern = pattern.lower()
    hostname = hostname.lower()
    if not pattern.startswith("*."):
        return pattern == hostname
    first, _, rest = hostname.partition(".")
    return first != "" and rest == pattern[2:]


def days_left(cert, now):
    """Whole days from now (seconds since 1970) until the certificate expires. Negative if it already has."""
    return int((ssl.cert_time_to_seconds(cert["notAfter"]) - now) // DAY)


def certificate_problems(cert, hostname, now):
    """Return a list of problems: 'not valid yet', 'expired' and 'wrong host name', in that order. Empty if it's fine."""
    problems = []
    if now < ssl.cert_time_to_seconds(cert["notBefore"]):
        problems.append("not valid yet")
    if now > ssl.cert_time_to_seconds(cert["notAfter"]):
        problems.append("expired")
    matched = False
    for name in dns_names(cert):
        if hostname_matches(name, hostname):
            matched = True
    if not matched:
        problems.append("wrong host name")
    return problems


if __name__ == "__main__":
    now = ssl.cert_time_to_seconds("Oct 26 12:00:00 2026 GMT")
    print(dns_names(EXAMPLE_CERT), issuer_name(EXAMPLE_CERT))
    print(days_left(EXAMPLE_CERT, now))
    for host in ["example.com", "www.example.com", "shop.www.example.com", "example.org"]:
        print(host, certificate_problems(EXAMPLE_CERT, host, now))
    print(certificate_problems(EXAMPLE_CERT, "example.com", ssl.cert_time_to_seconds("Jan 10 09:00:00 2027 GMT")))
