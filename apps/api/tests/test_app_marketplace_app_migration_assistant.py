from app.services.app_marketplace_app_migration_assistant import detect_breaking_changes, build_migration_guide

def test_detect():
    changes = detect_breaking_changes(
        old_manifest={"scopes": ["read", "write"], "events": ["install"], "min_api_version": "v1"},
        new_manifest={"scopes": ["read"], "events": ["install", "update"], "min_api_version": "v2"})
    types = [c["type"] for c in changes]
    assert "scope_removed" in types
    assert "api_version_change" in types

def test_no_changes():
    changes = detect_breaking_changes(old_manifest={"scopes": ["read"]}, new_manifest={"scopes": ["read"]})
    assert len(changes) == 0

def test_guide():
    changes = [{"type": "scope_removed", "detail": "write removed", "severity": "high"}]
    g = build_migration_guide(changes=changes, app_name="App")
    assert g["total_steps"] == 1
    assert g["estimated_effort"] == "high"
