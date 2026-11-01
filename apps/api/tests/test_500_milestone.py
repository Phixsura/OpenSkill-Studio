"""Tests to reach 500 test milestone — final coverage gaps."""

import pytest

from app.services.app_compatibility import check_upgrade_compatibility, parse_semver


def test_semver_with_build_metadata():
    """Semver with build metadata parses correctly."""
    assert parse_semver("1.0.0+build.123") == (1, 0, 0)


def test_compatibility_both_empty_permissions():
    """Both manifests with empty permissions = compatible."""
    report = check_upgrade_compatibility(
        {"permissions": [], "schema_version": "1.0"},
        {"permissions": [], "schema_version": "1.0"},
    )
    assert report["compatible"] is True
    assert report["permissions_added"] == []
    assert report["permissions_removed"] == []
    assert report["breaking_changes"] == []
    assert report["warnings"] == []
