"""Focused SSRF tests for manifest validation."""

from app.services.manifest_validator import validate_manifest


def test_ssrf_127_0_0_1():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": ["127.0.0.1"]}}})
    assert any("private" in e.lower() or "Blocked" in e for e in r.errors)

def test_ssrf_10_0_0_1():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": ["10.0.0.1"]}}})
    assert any("private" in e.lower() or "Blocked" in e for e in r.errors)

def test_ssrf_192_168():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": ["192.168.1.1"]}}})
    assert any("private" in e.lower() or "Blocked" in e for e in r.errors)

def test_ssrf_172_16():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": ["172.16.0.1"]}}})
    assert any("private" in e.lower() or "Blocked" in e for e in r.errors)

def test_ssrf_ipv6_loopback():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": ["::1"]}}})
    assert any("private" in e.lower() or "Blocked" in e for e in r.errors)

def test_ssrf_metadata_google():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": ["metadata.google.internal"]}}})
    assert any("internal" in e.lower() or "Blocked" in e for e in r.errors)

def test_ssrf_aws_metadata():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": ["169.254.169.254"]}}})
    assert any("private" in e.lower() or "Blocked" in e for e in r.errors)

def test_ssrf_public_domain_allowed():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": ["api.stripe.com"]}}})
    ssrf = [e for e in r.errors if "Blocked" in e or "private" in e.lower()]
    assert ssrf == []

def test_ssrf_localhost_suffix():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": ["evil.localhost"]}}})
    assert any("internal" in e.lower() or "Blocked" in e for e in r.errors)

def test_ssrf_non_string_host():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": [123]}}})
    assert any("string" in e for e in r.errors)
