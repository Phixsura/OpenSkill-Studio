"""Combined SSRF protection — manifest + event dispatch both block same IPs."""

import pytest
from app.services.event_dispatch import _is_safe_url
from app.services.manifest_validator import validate_manifest

BLOCKED = ["127.0.0.1", "10.0.0.1", "192.168.1.1", "169.254.169.254", "localhost"]

@pytest.mark.parametrize("host", BLOCKED)
def test_event_dispatch_blocks(host):
    assert _is_safe_url(f"http://{host}/hook") is False

@pytest.mark.parametrize("host", BLOCKED)
def test_manifest_blocks(host):
    m = {
        "schema_version": "1.0",
        "app": {"name": "X", "slug": "ssrf-combined", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
                     "network": {"allowed_hosts": [host], "egress_policy": "allowlist"}},
    }
    r = validate_manifest(m)
    assert not r.valid or len(r.errors) > 0
