"""Manifest validator SSRF IP range tests."""

import pytest
from app.services.manifest_validator import validate_manifest

BASE = {
    "schema_version": "1.0",
    "app": {"name": "X", "slug": "test-ssrf", "version": "1.0.0", "category": "connector"},
    "permissions": ["read:cohorts"],
}

BLOCKED_IPS = [
    "127.0.0.1", "10.0.0.1", "172.16.0.1", "192.168.1.1",
    "169.254.169.254", "0.0.0.0", "::1",
]

@pytest.mark.parametrize("ip", BLOCKED_IPS)
def test_blocked_ip_in_allowed_hosts(ip):
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
         "network": {"allowed_hosts": [ip], "egress_policy": "allowlist"}}}
    r = validate_manifest(m)
    assert not r.valid or len(r.errors) > 0

BLOCKED_HOSTNAMES = ["localhost", "metadata.google.internal"]

@pytest.mark.parametrize("host", BLOCKED_HOSTNAMES)
def test_blocked_hostname(host):
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
         "network": {"allowed_hosts": [host], "egress_policy": "allowlist"}}}
    r = validate_manifest(m)
    assert not r.valid or len(r.errors) > 0

SAFE_HOSTS = ["api.example.com", "hooks.slack.com", "webhook.site"]

@pytest.mark.parametrize("host", SAFE_HOSTS)
def test_safe_host_allowed(host):
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
         "network": {"allowed_hosts": [host], "egress_policy": "allowlist"}}}
    r = validate_manifest(m)
    host_errors = [e for e in r.errors if "host" in e.lower() or "block" in e.lower()]
    assert host_errors == []
