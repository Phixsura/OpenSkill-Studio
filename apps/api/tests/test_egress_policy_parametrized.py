"""Parametrized egress policy validation."""

import pytest
from app.services.manifest_validator import validate_manifest

VALID_POLICIES = ["allowlist", "deny_all"]
INVALID_POLICIES = ["allow_all", "open", "none", "permit"]

@pytest.mark.parametrize("policy", VALID_POLICIES)
def test_valid_egress(policy):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"egress_policy": policy}}})
    warns = [w for w in r.warnings if "egress" in w]
    assert warns == []

@pytest.mark.parametrize("policy", INVALID_POLICIES)
def test_invalid_egress(policy):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"egress_policy": policy}}})
    assert any("egress" in w for w in r.warnings)
