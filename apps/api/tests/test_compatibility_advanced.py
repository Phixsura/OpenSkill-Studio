"""Advanced compatibility checker tests."""

from app.services.app_compatibility import (
    check_upgrade_compatibility,
    is_compatible,
    parse_semver,
)


def test_semver_large_numbers():
    assert parse_semver("100.200.300") == (100, 200, 300)

def test_semver_zero():
    assert parse_semver("0.0.0") == (0, 0, 0)

def test_compatible_exact_match():
    assert is_compatible("1.0.0") is True

def test_compatible_lower():
    assert is_compatible("0.0.1") is True

def test_incompatible_major():
    assert is_compatible("2.0.0") is False

def test_upgrade_add_ui_surface():
    old = {"permissions": [], "ui_extensions": [{"surface": "dashboard_card"}]}
    new = {"permissions": [], "ui_extensions": [{"surface": "dashboard_card"}, {"surface": "cohort_tool"}]}
    report = check_upgrade_compatibility(old, new)
    assert report["compatible"] is True

def test_upgrade_change_egress_policy():
    old = {"permissions": [], "sandbox": {"network": {"egress_policy": "allowlist"}}}
    new = {"permissions": [], "sandbox": {"network": {"egress_policy": "deny_all"}}}
    report = check_upgrade_compatibility(old, new)
    assert report["compatible"] is True  # policy change is not breaking

def test_upgrade_add_event_subscription():
    old = {"permissions": [], "event_subscriptions": ["submission.completed"]}
    new = {"permissions": [], "event_subscriptions": ["submission.completed", "pack.published"]}
    report = check_upgrade_compatibility(old, new)
    assert report["compatible"] is True

def test_upgrade_remove_multiple_permissions():
    old = {"permissions": ["read:cohorts", "write:projects", "read:skills"]}
    new = {"permissions": ["read:cohorts"]}
    report = check_upgrade_compatibility(old, new)
    assert len(report["permissions_removed"]) == 2

def test_upgrade_add_multiple_secrets():
    old = {"permissions": [], "secrets": []}
    new = {"permissions": [], "secrets": [
        {"key": "KEY_A", "required": True},
        {"key": "KEY_B", "required": True},
    ]}
    report = check_upgrade_compatibility(old, new)
    assert any("KEY_A" in w or "KEY_B" in w for w in report["warnings"])
