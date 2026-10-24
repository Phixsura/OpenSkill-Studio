from app.services.app_manifest_linter import lint_manifest

def test_no_description():
    s = lint_manifest({"app": {"name": "X"}})
    assert any("description" in r["message"].lower() for r in s)

def test_many_perms():
    s = lint_manifest({"app": {"description": "X"}, "permissions": [f"read:r{i}" for i in range(20)]})
    assert any("permissions" in r["field"] for r in s)

def test_no_config_schema():
    s = lint_manifest({"app": {"description": "X"}, "permissions": []})
    assert any("config_schema" in r["field"] for r in s)

def test_secret_no_description():
    s = lint_manifest({"app": {"description": "X"}, "permissions": [], "config_schema": {}, "secrets": [{"key": "API_KEY"}]})
    assert any("API_KEY" in r["message"] for r in s)

def test_clean_manifest():
    s = lint_manifest({"app": {"description": "Good app"}, "permissions": ["read:cohorts"], "config_schema": {"type": "object"}, "secrets": [{"key": "K", "description": "d"}]})
    assert len(s) == 0 or all(r["level"] == "info" for r in s)
