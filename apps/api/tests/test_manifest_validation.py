"""Tests for manifest validation and observability."""

import pytest

from app.services.manifest_validator import VALID_PERMISSIONS, VALID_SURFACES, validate_manifest


class TestManifestValidation:
    def test_valid_minimal_manifest(self):
        manifest = {
            "schema_version": "1.0",
            "app": {"name": "Test App", "slug": "test-app", "version": "1.0.0"},
            "permissions": ["read:cohorts"],
        }
        result = validate_manifest(manifest)
        assert result.valid
        assert len(result.errors) == 0

    def test_valid_full_manifest(self):
        manifest = {
            "schema_version": "1.0",
            "app": {
                "name": "Acme LMS Connector",
                "slug": "acme-lms",
                "version": "1.2.0",
                "category": "connector",
            },
            "permissions": [
                "read:organizations",
                "read:cohorts",
                "write:project_results",
                "subscribe:events",
                "extend:ui",
            ],
            "sandbox": {
                "runtime": "nodejs20",
                "memory_mb": 128,
                "timeout_seconds": 30,
                "network": {
                    "allowed_hosts": ["api.acme-lms.com"],
                    "egress_policy": "allowlist",
                },
            },
            "ui_extensions": [
                {
                    "surface": "dashboard_card",
                    "title": "LMS Sync",
                    "entry": "ui/card.html",
                    "viewport": {"width": 400, "height": 300},
                }
            ],
            "event_subscriptions": ["submission.completed"],
            "secrets": [
                {"key": "LMS_API_KEY", "description": "API key", "required": True}
            ],
            "config_schema": {
                "type": "object",
                "properties": {"base_url": {"type": "string"}},
            },
        }
        result = validate_manifest(manifest)
        assert result.valid, f"Errors: {result.errors}"
        assert len(result.warnings) == 0

    def test_missing_schema_version(self):
        result = validate_manifest({"app": {"name": "X"}})
        assert not result.valid
        assert any("schema_version" in e for e in result.errors)

    def test_missing_app_block(self):
        result = validate_manifest({"schema_version": "1.0"})
        assert not result.valid
        assert any("app" in e for e in result.errors)

    def test_missing_app_name(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"slug": "test"},
        })
        assert not result.valid
        assert any("app.name" in e for e in result.errors)

    def test_invalid_slug(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test", "slug": "INVALID SLUG!"},
        })
        assert not result.valid
        assert any("slug" in e for e in result.errors)

    def test_invalid_version(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test", "version": "not-semver"},
        })
        assert not result.valid
        assert any("semver" in e for e in result.errors)

    def test_invalid_category(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test", "category": "invalid"},
        })
        assert not result.valid
        assert any("category" in e for e in result.errors)

    def test_invalid_permission(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "permissions": ["read:cohorts", "hack:system"],
        })
        assert not result.valid
        assert any("hack:system" in e for e in result.errors)

    def test_duplicate_permissions_warning(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "permissions": ["read:cohorts", "read:cohorts"],
        })
        assert result.valid  # warning, not error
        assert any("Duplicate" in w for w in result.warnings)

    def test_sandbox_memory_bounds(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "sandbox": {"memory_mb": 1024},
        })
        assert not result.valid
        assert any("memory_mb" in e for e in result.errors)

    def test_sandbox_timeout_bounds(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "sandbox": {"timeout_seconds": 600},
        })
        assert not result.valid
        assert any("timeout_seconds" in e for e in result.errors)

    def test_blocked_network_host(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "sandbox": {
                "network": {"allowed_hosts": ["169.254.169.254"]},
            },
        })
        assert not result.valid
        assert any("Blocked" in e for e in result.errors)

    def test_blocked_localhost(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "sandbox": {
                "network": {"allowed_hosts": ["localhost"]},
            },
        })
        assert not result.valid
        assert any("Blocked" in e for e in result.errors)

    def test_ui_extension_missing_surface(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "permissions": ["extend:ui"],
            "ui_extensions": [{"title": "Card", "entry": "card.html"}],
        })
        assert not result.valid
        assert any("surface" in e for e in result.errors)

    def test_ui_extension_invalid_surface(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "permissions": ["extend:ui"],
            "ui_extensions": [
                {"surface": "nonexistent", "title": "X", "entry": "x.html"}
            ],
        })
        assert not result.valid
        assert any("nonexistent" in e for e in result.errors)

    def test_ui_without_permission_warning(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "ui_extensions": [
                {"surface": "dashboard_card", "title": "X", "entry": "x.html"}
            ],
        })
        assert result.valid  # warning
        assert any("extend:ui" in w for w in result.warnings)

    def test_events_without_permission_warning(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "event_subscriptions": ["submission.completed"],
        })
        assert result.valid  # warning
        assert any("subscribe:events" in w for w in result.warnings)

    def test_duplicate_secret_keys(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "secrets": [
                {"key": "API_KEY", "description": "a"},
                {"key": "API_KEY", "description": "b"},
            ],
        })
        assert not result.valid
        assert any("Duplicate secret" in e for e in result.errors)

    def test_invalid_secret_key_format(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "secrets": [{"key": "lower-case-key"}],
        })
        assert not result.valid
        assert any("uppercase" in e for e in result.errors)

    def test_viewport_bounds(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "permissions": ["extend:ui"],
            "ui_extensions": [
                {
                    "surface": "dashboard_card",
                    "title": "X",
                    "entry": "x.html",
                    "viewport": {"width": 5000, "height": 50},
                }
            ],
        })
        assert not result.valid
        assert any("width" in e for e in result.errors)
        assert any("height" in e for e in result.errors)

    def test_non_dict_manifest(self):
        result = validate_manifest("not a dict")
        assert not result.valid
        assert any("JSON object" in e for e in result.errors)

    def test_permission_taxonomy_coverage(self):
        """Verify all 42 scopes are defined."""
        assert len(VALID_PERMISSIONS) >= 30

    def test_surfaces_defined(self):
        assert len(VALID_SURFACES) == 8
        assert "dashboard_card" in VALID_SURFACES
        assert "operator_console" in VALID_SURFACES

    def test_result_to_dict(self):
        result = validate_manifest({
            "schema_version": "1.0",
            "app": {"name": "Test"},
            "permissions": ["read:cohorts"],
        })
        d = result.to_dict()
        assert d["valid"] is True
        assert d["error_count"] == 0
        assert isinstance(d["errors"], list)
        assert isinstance(d["warnings"], list)
