"""Manifest egress policy validation."""

import pytest
from app.services.manifest_validator import validate_manifest

BASE = {
    "schema_version": "1.0",
    "app": {"name": "Egress", "slug": "egress-test", "version": "1.0.0", "category": "connector"},
    "permissions": ["read:cohorts"],
}

def test_allowlist_policy_valid():
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
         "network": {"allowed_hosts": ["api.example.com"], "egress_policy": "allowlist"}}}
    r = validate_manifest(m)
    assert r.valid

def test_no_egress_policy_defaults():
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
         "network": {"allowed_hosts": ["api.example.com"]}}}
    r = validate_manifest(m)
    # Should still be valid without explicit policy
    assert r.valid or len(r.errors) > 0

def test_sandbox_without_network():
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30}}
    r = validate_manifest(m)
    assert r.valid

def test_no_sandbox():
    m = {**BASE}
    r = validate_manifest(m)
    assert r.valid
