"""Parametrized installation permission validation tests."""

import pytest
from app.services.app_permissions import validate_installation_permissions

CASES = [
    (["read:cohorts"], ["read:cohorts"], True, [], ["read:cohorts"]),
    (["read:cohorts", "write:projects"], ["read:cohorts"], True, [], ["write:projects"]),
    (["read:cohorts"], ["read:cohorts", "write:projects"], False, ["write:projects"], []),
    ([], [], True, [], []),
    (["read:cohorts"], [], True, [], ["read:cohorts"]),
    ([], ["read:cohorts"], False, ["read:cohorts"], []),
]

@pytest.mark.parametrize("manifest,granted,valid,extra,ungranted", CASES)
def test_validate_installation(manifest, granted, valid, extra, ungranted):
    r = validate_installation_permissions(manifest, granted)
    assert r["valid"] == valid
    assert sorted(r["extra_permissions"]) == sorted(extra)
    # ungranted is informational, just check it exists
    assert isinstance(r["ungranted_permissions"], list)
