"""SSRF DNS resolution — _is_safe_url with various URL formats."""

import pytest
from app.services.event_dispatch import _is_safe_url

URL_BYPASS_ATTEMPTS = [
    "http://0x7f000001/",         # hex encoded 127.0.0.1
    "http://2130706433/",          # decimal 127.0.0.1
    "http://127.1/",              # shortened loopback
    "http://[0:0:0:0:0:0:0:1]/", # full IPv6 loopback
    "http://[::]/"  ,             # IPv6 any
]

@pytest.mark.parametrize("url", URL_BYPASS_ATTEMPTS)
def test_bypass_attempts_blocked(url):
    """Common SSRF bypass techniques should be blocked."""
    assert _is_safe_url(url) is False

SCHEME_ATTACKS = [
    "gopher://evil.com",
    "file:///etc/passwd",
    "dict://evil.com:11211",
]

@pytest.mark.parametrize("url", SCHEME_ATTACKS)
def test_non_http_schemes_blocked(url):
    assert _is_safe_url(url) is False
