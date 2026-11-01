"""Advanced permission validation tests."""

from app.services.app_permissions import (
    PATH_PERMISSION_MAP,
    WRITE_PERMISSION_MAP,
    check_permission,
    get_missing_permissions,
    get_permission_summary,
    validate_installation_permissions,
)


def test_all_read_resources_mapped():
    assert len(PATH_PERMISSION_MAP) >= 10
    for resource, perm in PATH_PERMISSION_MAP.items():
        assert perm.startswith("read:"), f"{resource} → {perm} should start with read:"


def test_all_write_resources_mapped():
    assert len(WRITE_PERMISSION_MAP) >= 8
    for resource, perm in WRITE_PERMISSION_MAP.items():
        assert perm.startswith("write:") or perm.startswith("read:"), f"{resource} → {perm}"


def test_read_write_resources_overlap():
    read_resources = set(PATH_PERMISSION_MAP.keys())
    write_resources = set(WRITE_PERMISSION_MAP.keys())
    common = read_resources & write_resources
    assert len(common) >= 5  # most resources have both


def test_check_all_read_resources():
    for resource, perm in PATH_PERMISSION_MAP.items():
        assert check_permission([perm], resource, is_write=False)
        assert not check_permission([], resource, is_write=False)


def test_check_all_write_resources():
    for resource, perm in WRITE_PERMISSION_MAP.items():
        assert check_permission([perm], resource, is_write=True)
        assert not check_permission([], resource, is_write=True)


def test_missing_single():
    missing = get_missing_permissions(["read:cohorts"], ["read:cohorts", "write:projects"])
    assert missing == ["write:projects"]


def test_missing_none():
    missing = get_missing_permissions(["read:cohorts", "write:projects"], ["read:cohorts"])
    assert missing == []


def test_missing_all():
    missing = get_missing_permissions([], ["read:cohorts", "write:projects"])
    assert len(missing) == 2


def test_validate_exact_match():
    r = validate_installation_permissions(["read:cohorts"], ["read:cohorts"])
    assert r["valid"] is True
    assert r["extra_permissions"] == []
    assert r["ungranted_permissions"] == []


def test_validate_subset():
    r = validate_installation_permissions(["read:cohorts", "read:projects"], ["read:cohorts"])
    assert r["valid"] is True
    assert "read:projects" in r["ungranted_permissions"]


def test_validate_superset_invalid():
    r = validate_installation_permissions(["read:cohorts"], ["read:cohorts", "write:projects"])
    assert r["valid"] is False
    assert "write:projects" in r["extra_permissions"]


def test_summary_categories():
    perms = ["read:cohorts", "read:projects", "write:projects", "subscribe:events", "extend:ui", "run:background_jobs", "export:analytics"]
    s = get_permission_summary(perms)
    assert s["total"] == 7
    assert s["read_count"] == 2
    assert s["write_count"] == 1
    assert s["special_count"] == 4
    assert len(s["categories"]) >= 5
