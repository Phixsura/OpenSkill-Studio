"""Parametrized runtime validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest, VALID_RUNTIMES

@pytest.mark.parametrize("runtime", sorted(VALID_RUNTIMES))
def test_valid_runtime(runtime):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"runtime": runtime}})
    warns = [w for w in r.warnings if "runtime" in w]
    assert warns == []

INVALID_RUNTIMES = ["deno2", "bun1", "ruby3", "java21", "go1.22"]

@pytest.mark.parametrize("runtime", INVALID_RUNTIMES)
def test_invalid_runtime_warns(runtime):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"runtime": runtime}})
    assert any("runtime" in w for w in r.warnings)
