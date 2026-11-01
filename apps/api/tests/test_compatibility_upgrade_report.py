"""Compatibility upgrade report detailed tests."""

import pytest
from app.services.app_compatibility import check_upgrade_compatibility

UPGRADE_CASES = [
    # No changes
    ({"permissions": ["read:cohorts"]}, {"permissions": ["read:cohorts"]}, True, [], []),
    # Add permission
    ({"permissions": ["read:cohorts"]}, {"permissions": ["read:cohorts", "write:cohorts"]}, True, ["write:cohorts"], []),
    # Remove permission
    ({"permissions": ["read:cohorts", "write:cohorts"]}, {"permissions": ["read:cohorts"]}, True, [], ["write:cohorts"]),
    # Both add and remove
    ({"permissions": ["read:cohorts"]}, {"permissions": ["write:projects"]}, True, ["write:projects"], ["read:cohorts"]),
    # Empty to permissions
    ({}, {"permissions": ["read:cohorts"]}, True, [], []),
    # Permissions to empty
    ({"permissions": ["read:cohorts"]}, {}, True, [], []),
]

@pytest.mark.parametrize("old,new,compat,added,removed", UPGRADE_CASES,
    ids=lambda x: str(x)[:40])
def test_upgrade_report(old, new, compat, added, removed):
    r = check_upgrade_compatibility(old, new)
    assert r["compatible"] is compat
    assert set(r["permissions_added"]) == set(added)
    assert set(r["permissions_removed"]) == set(removed)

def test_none_manifests():
    r = check_upgrade_compatibility(None, None)
    assert r["compatible"] is True
    assert r["breaking_changes"] == []

def test_old_none():
    r = check_upgrade_compatibility(None, {"permissions": ["read:cohorts"]})
    assert r["compatible"] is True

def test_new_none():
    r = check_upgrade_compatibility({"permissions": ["read:cohorts"]}, None)
    assert r["compatible"] is True

def test_report_keys():
    r = check_upgrade_compatibility({}, {})
    assert "compatible" in r
    assert "breaking_changes" in r
    assert "warnings" in r
    assert "permissions_added" in r
    assert "permissions_removed" in r
