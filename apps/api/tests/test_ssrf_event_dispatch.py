"""SSRF protection tests for event dispatch."""

import pytest
from app.services.event_dispatch import _is_safe_url

UNSAFE = ["https://localhost", "https://127.0.0.1", "https://169.254.169.254",
    "https://metadata.google.internal", "http://example.com", "", "ftp://x.com",
    "not-a-url", "https://10.0.0.1", "https://192.168.1.1", "https://172.16.0.1"]

@pytest.mark.parametrize("url", UNSAFE)
def test_unsafe_url(url):
    assert _is_safe_url(url) is False
