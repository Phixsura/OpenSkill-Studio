"""Parametrized SSRF protection tests."""

import pytest
from app.services.manifest_validator import validate_manifest

BLOCKED_HOSTS = [
    "localhost", "127.0.0.1", "10.0.0.1", "10.255.255.255",
    "172.16.0.1", "172.31.255.255", "192.168.0.1", "192.168.255.255",
    "169.254.169.254", "::1", "0.0.0.0", "metadata.google.internal",
    "evil.localhost", "sub.internal",
]

@pytest.mark.parametrize("host", BLOCKED_HOSTS)
def test_blocked_host(host):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "sandbox": {"network": {"allowed_hosts": [host]}}})
    ssrf_errors = [e for e in r.errors if "Blocked" in e or "private" in e.lower() or "internal" in e.lower()]
    assert len(ssrf_errors) >= 1, f"Host '{host}' should be blocked"

ALLOWED_HOSTS = ["api.example.com", "hooks.slack.com", "api.stripe.com"]

@pytest.mark.parametrize("host", ALLOWED_HOSTS)
def test_allowed_host(host):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "sandbox": {"network": {"allowed_hosts": [host]}}})
    ssrf_errors = [e for e in r.errors if "Blocked" in e or "private" in e.lower()]
    assert ssrf_errors == [], f"Host '{host}' should be allowed"
