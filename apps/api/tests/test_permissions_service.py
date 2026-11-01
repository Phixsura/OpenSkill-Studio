"""Tests for app permission validation service."""

from app.services.app_permissions import (
    check_permission,
    get_missing_permissions,
    get_permission_summary,
    validate_installation_permissions,
)


def test_check_read_permission_granted():
    assert check_permission(["read:cohorts"], "cohorts") is True


def test_check_read_permission_denied():
    assert check_permission(["read:projects"], "cohorts") is False


def test_check_write_permission():
    assert check_permission(["write:projects"], "projects", is_write=True) is True
    assert check_permission(["read:projects"], "projects", is_write=True) is False


def test_check_unknown_resource():
    assert check_permission([], "unknown_resource") is True


def test_get_missing_permissions():
    granted = ["read:cohorts", "read:projects"]
    required = ["read:cohorts", "read:projects", "write:projects"]
    missing = get_missing_permissions(granted, required)
    assert missing == ["write:projects"]


def test_get_missing_permissions_none():
    missing = get_missing_permissions(["read:cohorts"], ["read:cohorts"])
    assert missing == []


def test_validate_installation_permissions_valid():
    result = validate_installation_permissions(
        manifest_permissions=["read:cohorts", "read:projects"],
        granted_permissions=["read:cohorts"],
    )
    assert result["valid"] is True
    assert result["extra_permissions"] == []
    assert "read:projects" in result["ungranted_permissions"]


def test_validate_installation_permissions_extra():
    result = validate_installation_permissions(
        manifest_permissions=["read:cohorts"],
        granted_permissions=["read:cohorts", "write:projects"],
    )
    assert result["valid"] is False
    assert "write:projects" in result["extra_permissions"]


def test_permission_summary():
    perms = ["read:cohorts", "read:projects", "write:projects", "subscribe:events", "extend:ui"]
    summary = get_permission_summary(perms)
    assert summary["total"] == 5
    assert summary["read_count"] == 2
    assert summary["write_count"] == 1
    assert summary["special_count"] == 2
    assert "read" in summary["categories"]
    assert "subscribe" in summary["categories"]


def test_permission_summary_empty():
    summary = get_permission_summary([])
    assert summary["total"] == 0
    assert summary["read_count"] == 0
