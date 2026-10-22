"""Manifest runtime/sandbox validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

BASE = {
    "schema_version": "1.0",
    "app": {"name": "Test", "slug": "test-rt", "version": "1.0.0", "category": "connector"},
    "permissions": ["read:cohorts"],
}

VALID_RUNTIMES = ["python3.11", "python3.12", "nodejs20"]

@pytest.mark.parametrize("runtime", VALID_RUNTIMES)
def test_valid_runtime(runtime):
    m = {**BASE, "sandbox": {"runtime": runtime, "memory_mb": 128, "timeout_seconds": 30}}
    r = validate_manifest(m)
    runtime_errors = [e for e in r.errors if "runtime" in e.lower()]
    assert runtime_errors == []

MEMORY_CASES = [
    (64, True),
    (128, True),
    (256, True),
    (512, True),
]

@pytest.mark.parametrize("mb,valid", MEMORY_CASES)
def test_memory_limits(mb, valid):
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": mb, "timeout_seconds": 30}}
    r = validate_manifest(m)
    if valid:
        mem_errors = [e for e in r.errors if "memory" in e.lower()]
        assert mem_errors == []

TIMEOUT_CASES = [
    (10, True),
    (30, True),
    (60, True),
    (120, True),
]

@pytest.mark.parametrize("seconds,valid", TIMEOUT_CASES)
def test_timeout_limits(seconds, valid):
    m = {**BASE, "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": seconds}}
    r = validate_manifest(m)
    if valid:
        timeout_errors = [e for e in r.errors if "timeout" in e.lower()]
        assert timeout_errors == []
