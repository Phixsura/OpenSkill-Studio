"""Tests for app import validation and planning."""

from app.services.app_import import prepare_import_plan, validate_import_data


def test_validate_valid_import():
    data = {
        "export_version": "1.0",
        "app": {"name": "Test App", "slug": "test-app", "category": "connector"},
        "versions": [
            {"version": "1.0.0", "content_hash": "a" * 64, "manifest": {"schema_version": "1.0", "app": {"name": "Test"}, "permissions": []}},
        ],
    }
    result = validate_import_data(data)
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_missing_app():
    result = validate_import_data({"export_version": "1.0"})
    assert result["valid"] is False
    assert any("app" in e.lower() for e in result["errors"])


def test_validate_missing_name():
    result = validate_import_data({"export_version": "1.0", "app": {"slug": "test"}})
    assert result["valid"] is False
    assert any("name" in e for e in result["errors"])


def test_validate_missing_slug():
    result = validate_import_data({"export_version": "1.0", "app": {"name": "Test"}})
    assert result["valid"] is False
    assert any("slug" in e for e in result["errors"])


def test_validate_unknown_version():
    data = {"export_version": "2.0", "app": {"name": "T", "slug": "t"}, "versions": []}
    result = validate_import_data(data)
    assert result["valid"] is True  # warning, not error
    assert any("2.0" in w for w in result["warnings"])


def test_validate_version_missing_hash():
    data = {
        "export_version": "1.0",
        "app": {"name": "T", "slug": "t"},
        "versions": [{"version": "1.0.0"}],
    }
    result = validate_import_data(data)
    assert any("content_hash" in e for e in result["errors"])


def test_validate_bad_manifest_in_version():
    data = {
        "export_version": "1.0",
        "app": {"name": "T", "slug": "t"},
        "versions": [
            {"version": "1.0.0", "content_hash": "a" * 64, "manifest": {"permissions": ["hack:system"]}},
        ],
    }
    result = validate_import_data(data)
    # Manifest issues are warnings, not errors
    assert any("manifest" in w.lower() for w in result["warnings"])


def test_prepare_import_plan():
    data = {
        "app": {"name": "Test", "slug": "test", "category": "connector"},
        "versions": [
            {"version": "1.0.0", "manifest": {"schema_version": "1.0"}},
            {"version": "2.0.0"},
        ],
        "ui_extensions": [
            {"surface": "dashboard_card", "title": "Card"},
        ],
    }
    plan = prepare_import_plan(data)
    assert plan["summary"]["app_count"] == 1
    assert plan["summary"]["version_count"] == 2
    assert plan["summary"]["ui_extension_count"] == 1
    assert plan["plan"]["app"]["slug"] == "test"
    assert len(plan["plan"]["versions"]) == 2
    assert plan["plan"]["versions"][0]["has_manifest"] is True
    assert plan["plan"]["versions"][1]["has_manifest"] is False


def test_prepare_empty_plan():
    plan = prepare_import_plan({"app": {}, "versions": [], "ui_extensions": []})
    assert plan["summary"]["version_count"] == 0
