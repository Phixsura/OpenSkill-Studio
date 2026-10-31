"""Parametrized sandbox config validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

VALID_MEMORY = [32, 64, 128, 256, 512]
INVALID_MEMORY = [0, 16, 31, 513, 1024, -1]
VALID_TIMEOUT = [1, 5, 30, 60, 300]
INVALID_TIMEOUT = [0, -1, 301, 600, 1000]

@pytest.mark.parametrize("mem", VALID_MEMORY)
def test_valid_memory(mem):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"memory_mb": mem}})
    mem_errors = [e for e in r.errors if "memory_mb" in e]
    assert mem_errors == [], f"memory_mb={mem} rejected"

@pytest.mark.parametrize("mem", INVALID_MEMORY)
def test_invalid_memory(mem):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"memory_mb": mem}})
    assert any("memory_mb" in e for e in r.errors), f"memory_mb={mem} accepted"

@pytest.mark.parametrize("timeout", VALID_TIMEOUT)
def test_valid_timeout(timeout):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"timeout_seconds": timeout}})
    timeout_errors = [e for e in r.errors if "timeout_seconds" in e]
    assert timeout_errors == [], f"timeout_seconds={timeout} rejected"

@pytest.mark.parametrize("timeout", INVALID_TIMEOUT)
def test_invalid_timeout(timeout):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"timeout_seconds": timeout}})
    assert any("timeout_seconds" in e for e in r.errors), f"timeout_seconds={timeout} accepted"
