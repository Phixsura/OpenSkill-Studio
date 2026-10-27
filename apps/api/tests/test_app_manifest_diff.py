"""Tests for App Manifest Diff — field changes, permissions, config, severity."""

import pytest

from app.services.app_manifest_diff import (
    ChangeKind,
    ChangeSeverity,
    diff_manifests,
)

V1 = {
    "name": "LMS Connector",
    "description": "Sync grades with LMS",
    "version": "1.0.0",
    "permissions": ["read:skills", "read:projects"],
    "config_fields": {"api_url": "url", "timeout": "integer"},
    "extension_surfaces": ["ui_sidebar"],
    "icon_url": "https://example.com/icon.png",
    "min_platform_version": "1.0.0",
}

V2 = {
    "name": "LMS Connector",
    "description": "Sync grades and courses with any LMS system",
    "version": "2.0.0",
    "permissions": ["read:skills", "write:submissions"],
    "config_fields": {"api_url": "url", "batch_size": "integer"},
    "extension_surfaces": ["ui_sidebar", "ui_dashboard_widget"],
    "icon_url": "https://example.com/icon-v2.png",
    "min_platform_version": "2.0.0",
    "changelog": "Major update with course sync support",
}


class TestFieldChanges:
    def test_unchanged_field(self):
        result = diff_manifests(V1, V2)
        name_change = [c for c in result.changes if c.field_path == "name"][0]
        assert name_change.kind == ChangeKind.UNCHANGED

    def test_modified_field(self):
        result = diff_manifests(V1, V2)
        desc = [c for c in result.changes if c.field_path == "description"][0]
        assert desc.kind == ChangeKind.MODIFIED

    def test_added_field(self):
        result = diff_manifests(V1, V2)
        changelog = [c for c in result.changes if c.field_path == "changelog"]
        assert len(changelog) == 1
        assert changelog[0].kind == ChangeKind.ADDED

    def test_removed_field(self):
        old = {**V1, "deprecated_field": "old"}
        result = diff_manifests(old, V2)
        removed = [c for c in result.changes if c.field_path == "deprecated_field"]
        assert len(removed) == 1
        assert removed[0].kind == ChangeKind.REMOVED

    def test_total_changes(self):
        result = diff_manifests(V1, V2)
        assert result.total_changes > 0

    def test_identical_manifests(self):
        result = diff_manifests(V1, V1)
        assert result.total_changes == 0
        assert result.has_breaking is False


class TestPermissions:
    def test_added_permissions(self):
        result = diff_manifests(V1, V2)
        assert "write:submissions" in result.added_permissions

    def test_removed_permissions(self):
        result = diff_manifests(V1, V2)
        assert "read:projects" in result.removed_permissions

    def test_removed_permissions_breaking(self):
        result = diff_manifests(V1, V2)
        assert result.has_breaking is True

    def test_no_perm_changes(self):
        same = {**V1, "version": "1.0.1"}
        result = diff_manifests(V1, same)
        assert result.added_permissions == []
        assert result.removed_permissions == []


class TestConfigFields:
    def test_added_config(self):
        result = diff_manifests(V1, V2)
        assert "batch_size" in result.added_config_fields

    def test_removed_config(self):
        result = diff_manifests(V1, V2)
        assert "timeout" in result.removed_config_fields


class TestExtensionSurfaces:
    def test_added_surface(self):
        result = diff_manifests(V1, V2)
        assert "ui_dashboard_widget" in result.added_surfaces

    def test_removed_surface(self):
        old = {**V1, "extension_surfaces": ["ui_sidebar", "ui_settings"]}
        result = diff_manifests(old, V2)
        assert "ui_settings" in result.removed_surfaces


class TestSeverity:
    def test_patch_for_description(self):
        result = diff_manifests(V1, V2)
        desc = [c for c in result.changes if c.field_path == "description"][0]
        assert desc.severity == ChangeSeverity.PATCH

    def test_patch_for_icon(self):
        result = diff_manifests(V1, V2)
        icon = [c for c in result.changes if c.field_path == "icon_url"][0]
        assert icon.severity == ChangeSeverity.PATCH

    def test_breaking_for_min_platform_version(self):
        result = diff_manifests(V1, V2)
        mpv = [c for c in result.changes if c.field_path == "min_platform_version"][0]
        assert mpv.severity == ChangeSeverity.BREAKING

    def test_breaking_for_removed_permissions(self):
        result = diff_manifests(V1, V2)
        perm = [c for c in result.changes if c.field_path == "permissions"][0]
        assert perm.severity == ChangeSeverity.BREAKING

    def test_breaking_for_removed_config(self):
        result = diff_manifests(V1, V2)
        cfg = [c for c in result.changes if c.field_path == "config_fields"][0]
        assert cfg.severity == ChangeSeverity.BREAKING


class TestSummary:
    def test_summary_text(self):
        result = diff_manifests(V1, V2, "1.0.0", "2.0.0")
        assert "changes" in result.summary
        assert "breaking" in result.summary
        assert result.from_version == "1.0.0"
        assert result.to_version == "2.0.0"

    def test_summary_permission_counts(self):
        result = diff_manifests(V1, V2)
        assert "+1 permissions" in result.summary
        assert "-1 permissions" in result.summary
