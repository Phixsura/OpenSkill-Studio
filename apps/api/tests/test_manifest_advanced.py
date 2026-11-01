"""Advanced manifest validation tests covering all edge cases."""

from app.services.manifest_validator import validate_manifest


def test_valid_full_manifest():
    result = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "Full", "slug": "full-app", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "subscribe:events", "extend:ui"],
        "sandbox": {
            "runtime": "nodejs20", "memory_mb": 256, "timeout_seconds": 60,
            "network": {"allowed_hosts": ["api.example.com"], "egress_policy": "allowlist"},
        },
        "ui_extensions": [{"surface": "dashboard_card", "title": "Card", "entry": "card.html", "viewport": {"width": 400, "height": 300}}],
        "event_subscriptions": ["submission.completed"],
        "secrets": [{"key": "API_KEY", "description": "Key", "required": True}],
        "config_schema": {"type": "object", "properties": {"url": {"type": "string"}}},
    })
    assert result.valid
    assert result.errors == []

def test_memory_boundary_32():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"memory_mb": 32}})
    assert not any("memory_mb" in e for e in r.errors)

def test_memory_boundary_512():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"memory_mb": 512}})
    assert not any("memory_mb" in e for e in r.errors)

def test_memory_boundary_31():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"memory_mb": 31}})
    assert any("memory_mb" in e for e in r.errors)

def test_memory_boundary_513():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"memory_mb": 513}})
    assert any("memory_mb" in e for e in r.errors)

def test_timeout_boundary_1():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"timeout_seconds": 1}})
    assert not any("timeout_seconds" in e for e in r.errors)

def test_timeout_boundary_300():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"timeout_seconds": 300}})
    assert not any("timeout_seconds" in e for e in r.errors)

def test_timeout_boundary_0():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"timeout_seconds": 0}})
    assert any("timeout_seconds" in e for e in r.errors)

def test_timeout_boundary_301():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"timeout_seconds": 301}})
    assert any("timeout_seconds" in e for e in r.errors)

def test_viewport_width_boundaries():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": "dashboard_card", "title": "T", "entry": "t.html", "viewport": {"width": 99}}]})
    assert any("width" in e for e in r.errors)
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": "dashboard_card", "title": "T", "entry": "t.html", "viewport": {"width": 1921}}]})
    assert any("width" in e for e in r.errors)

def test_viewport_height_boundaries():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": "dashboard_card", "title": "T", "entry": "t.html", "viewport": {"height": 99}}]})
    assert any("height" in e for e in r.errors)

def test_all_valid_categories():
    for cat in ["connector", "workflow_adapter", "ui_extension", "analytics", "automation", "content_pack", "ecosystem_source"]:
        r = validate_manifest({"schema_version": "1.0", "app": {"name": "T", "category": cat}})
        assert not any("category" in e for e in r.errors), f"Category {cat} rejected"

def test_all_valid_surfaces():
    for surface in ["dashboard_card", "project_sidebar", "cohort_tool", "submission_panel", "registry_detail", "settings_page", "client_portal_widget", "operator_console"]:
        r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
            "ui_extensions": [{"surface": surface, "title": "T", "entry": "t.html"}]})
        assert not any(surface in e for e in r.errors), f"Surface {surface} rejected"

def test_schema_version_11():
    r = validate_manifest({"schema_version": "1.1", "app": {"name": "T"}})
    assert r.valid

def test_unknown_schema_version_warning():
    r = validate_manifest({"schema_version": "3.0", "app": {"name": "T"}})
    assert any("3.0" in w for w in r.warnings)

def test_non_string_permission():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": [123]})
    assert any("string" in e for e in r.errors)

def test_app_name_too_long():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "X" * 101}})
    assert any("100" in e for e in r.errors)
