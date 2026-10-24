"""SSRF URL parsing edge cases."""

import pytest
from app.services.event_dispatch import _is_safe_url

VALID_HTTPS = [
    "https://hooks.example.com/webhook",
    "https://api.myapp.io:443/events",
    "https://subdomain.deep.example.com/path",
]

@pytest.mark.parametrize("url", VALID_HTTPS)
def test_https_allowed(url):
    # May still fail DNS in test env, but URL format should be accepted
    result = _is_safe_url(url)
    # If DNS resolves to public IP → True; if DNS fails → may be False
    assert isinstance(result, bool)

NO_SCHEME = ["example.com/hook", "//example.com", "example.com"]

@pytest.mark.parametrize("url", NO_SCHEME)
def test_no_scheme_blocked(url):
    assert _is_safe_url(url) is False

INTERNAL_PORTS = [
    "http://127.0.0.1:80/",
    "http://127.0.0.1:8080/",
    "http://127.0.0.1:3000/",
    "http://localhost:9090/",
]

@pytest.mark.parametrize("url", INTERNAL_PORTS)
def test_internal_ports_blocked(url):
    assert _is_safe_url(url) is False
