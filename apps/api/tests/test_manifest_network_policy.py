"""Manifest network egress policy tests."""

import pytest
from app.services.manifest_validator import validate_manifest

BASE = {
    "schema_version": "1.0",
    "app": {"name": "Net", "slug": "net-test", "version": "1.0.0", "category": "connector"},
    "permissions": ["read:cohorts"],
}

def test_allowlist_policy():
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
         "network": {"allowed_hosts": ["api.example.com"], "egress_policy": "allowlist"}}}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_no_network_section():
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30}}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_empty_allowed_hosts():
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
         "network": {"allowed_hosts": [], "egress_policy": "allowlist"}}}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_multiple_allowed_hosts():
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30,
         "network": {"allowed_hosts": ["api1.com", "api2.com", "hooks.slack.com"], "egress_policy": "allowlist"}}}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"
