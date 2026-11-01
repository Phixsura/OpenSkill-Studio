"""App security scanner tests."""

import pytest
from app.services.app_security_scanner import scan_manifest

CLEAN = {"permissions": ["read:cohorts"], "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30}}

def test_clean_manifest():
    r = scan_manifest(CLEAN)
    assert r["passed"] is True
    assert r["risk_level"] == "none"

def test_excessive_permissions():
    m = {**CLEAN, "permissions": ["read:cohorts", "write:settings"]}
    r = scan_manifest(m)
    assert any(f["type"] == "excessive_permissions" for f in r["findings"])

def test_high_memory():
    m = {**CLEAN, "sandbox": {"runtime": "python3.12", "memory_mb": 1024, "timeout_seconds": 30}}
    r = scan_manifest(m)
    assert any(f["type"] == "high_memory" for f in r["findings"])

def test_long_timeout():
    m = {**CLEAN, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 300}}
    r = scan_manifest(m)
    assert any(f["type"] == "long_timeout" for f in r["findings"])

def test_dangerous_secret_name():
    m = {**CLEAN, "secrets": [{"key": "USER_PASSWORD"}]}
    r = scan_manifest(m)
    assert r["risk_level"] == "high"

def test_many_hosts():
    m = {**CLEAN, "sandbox": {"runtime": "x", "memory_mb": 128, "timeout_seconds": 30,
         "network": {"allowed_hosts": [f"host{i}.com" for i in range(15)]}}}
    r = scan_manifest(m)
    assert any(f["type"] == "many_hosts" for f in r["findings"])

def test_empty_manifest():
    r = scan_manifest({})
    assert r["passed"] is True

def test_total_findings():
    m = {**CLEAN, "permissions": ["write:settings"], "secrets": [{"key": "PASSWORD"}]}
    r = scan_manifest(m)
    assert r["total_findings"] >= 2
