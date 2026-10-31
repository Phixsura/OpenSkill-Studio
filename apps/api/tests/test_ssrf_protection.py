"""SSRF protection — _is_safe_url tests."""

import pytest
from app.services.event_dispatch import _is_safe_url

PRIVATE_IPS = [
    "http://127.0.0.1/hook",
    "http://127.0.0.255/hook",
    "http://10.0.0.1/hook",
    "http://10.255.255.255/hook",
    "http://172.16.0.1/hook",
    "http://172.31.255.255/hook",
    "http://192.168.0.1/hook",
    "http://192.168.255.255/hook",
    "http://[::1]/hook",
    "http://169.254.169.254/metadata",
    "http://0.0.0.0/hook",
]

SPECIAL_HOSTS = [
    "http://localhost/hook",
    "http://localhost:8080/hook",
]

@pytest.mark.parametrize("url", PRIVATE_IPS)
def test_private_ip_blocked(url):
    assert _is_safe_url(url) is False

@pytest.mark.parametrize("url", SPECIAL_HOSTS)
def test_special_host_blocked(url):
    assert _is_safe_url(url) is False

MALFORMED = [
    "",
    "not-a-url",
    "ftp://example.com",
    "file:///etc/passwd",
]

@pytest.mark.parametrize("url", MALFORMED)
def test_malformed_blocked(url):
    assert _is_safe_url(url) is False
