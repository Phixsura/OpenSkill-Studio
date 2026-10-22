"""Advanced import validation and plan tests."""

from app.services.app_import import prepare_import_plan, validate_import_data


def test_import_with_ui_extensions():
    data = {
        "export_version": "1.0",
        "app": {"name": "UI App", "slug": "ui-app"},
        "versions": [],
        "ui_extensions": [
            {"surface": "dashboard_card", "title": "Card", "entry_path": "card.html"},
            {"surface": "cohort_tool", "title": "Tool", "entry_path": "tool.html"},
        ],
    }
    result = validate_import_data(data)
    assert result["valid"] is True


def test_import_ui_extension_missing_surface():
    data = {
        "export_version": "1.0",
        "app": {"name": "T", "slug": "t"},
        "ui_extensions": [{"title": "No Surface"}],
    }
    result = validate_import_data(data)
    assert any("surface" in w for w in result["warnings"])


def test_import_ui_extension_missing_entry():
    data = {
        "export_version": "1.0",
        "app": {"name": "T", "slug": "t"},
        "ui_extensions": [{"surface": "dashboard_card", "title": "T"}],
    }
    result = validate_import_data(data)
    assert any("entry_path" in w for w in result["warnings"])


def test_import_multiple_versions():
    data = {
        "export_version": "1.0",
        "app": {"name": "T", "slug": "t"},
        "versions": [
            {"version": "1.0.0", "content_hash": "a" * 64},
            {"version": "2.0.0", "content_hash": "b" * 64},
            {"version": "3.0.0", "content_hash": "c" * 64},
        ],
    }
    result = validate_import_data(data)
    assert result["valid"] is True


def test_import_version_missing_version_field():
    data = {
        "export_version": "1.0",
        "app": {"name": "T", "slug": "t"},
        "versions": [{"content_hash": "a" * 64}],
    }
    result = validate_import_data(data)
    assert any("version" in e for e in result["errors"])


def test_import_non_list_versions():
    data = {
        "export_version": "1.0",
        "app": {"name": "T", "slug": "t"},
        "versions": "not a list",
    }
    result = validate_import_data(data)
    assert not result["valid"]


def test_plan_with_extensions():
    data = {
        "app": {"name": "Plan App", "slug": "plan", "category": "analytics"},
        "versions": [{"version": "1.0.0", "manifest": {"x": 1}}],
        "ui_extensions": [{"surface": "dashboard_card", "title": "Card"}],
    }
    plan = prepare_import_plan(data)
    assert plan["summary"]["app_count"] == 1
    assert plan["summary"]["version_count"] == 1
    assert plan["summary"]["ui_extension_count"] == 1
    assert plan["plan"]["app"]["category"] == "analytics"
    assert plan["plan"]["versions"][0]["has_manifest"] is True


def test_plan_no_versions():
    plan = prepare_import_plan({"app": {"name": "Empty"}, "versions": [], "ui_extensions": []})
    assert plan["summary"]["version_count"] == 0
    assert plan["summary"]["ui_extension_count"] == 0


def test_import_non_dict_version_entry():
    data = {
        "export_version": "1.0",
        "app": {"name": "T", "slug": "t"},
        "versions": ["not a dict"],
    }
    result = validate_import_data(data)
    assert any("object" in e for e in result["errors"])
