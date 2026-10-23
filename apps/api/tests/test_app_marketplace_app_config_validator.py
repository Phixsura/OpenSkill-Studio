from app.services.app_marketplace_app_config_validator import validate_manifest

def test_valid():
    m = {"name": "App", "version": "1.0.0", "description": "Desc",
         "author": "Alice", "entry_point": "index.ts", "icon": "icon.png", "category": "tools"}
    r = validate_manifest(manifest=m)
    assert r["valid"]
    assert r["error_count"] == 0
    assert r["warning_count"] == 0

def test_missing_fields():
    r = validate_manifest(manifest={"name": "App"})
    assert not r["valid"]
    assert r["error_count"] == 4

def test_bad_version():
    m = {"name": "A", "version": "abc", "description": "D", "author": "B", "entry_point": "x.ts"}
    r = validate_manifest(manifest=m)
    assert not r["valid"]
    assert any(e["field"] == "version" for e in r["errors"])

def test_warnings():
    m = {"name": "A", "version": "1.0.0", "description": "D", "author": "B", "entry_point": "x.ts"}
    r = validate_manifest(manifest=m)
    assert r["valid"]
    assert r["warning_count"] == 2  # no icon, no category
