from app.services.app_marketplace_app_app_app_app_app_app_app_schema_version import compare_schemas, version_history

def test_compare_breaking():
    r = compare_schemas(
        {"fields": {"name": "string", "age": "int"}},
        {"fields": {"name": "string", "email": "string"}})
    assert r["breaking"]
    assert "email" in r["added"]
    assert "age" in r["removed"]
    assert r["suggested_bump"] == "major"

def test_compare_minor():
    r = compare_schemas(
        {"fields": {"name": "string"}},
        {"fields": {"name": "string", "bio": "string"}})
    assert not r["breaking"]
    assert r["suggested_bump"] == "minor"

def test_history():
    r = version_history([
        {"version": "1.0", "released_at": "2026-01-01"},
        {"version": "2.0", "released_at": "2026-06-01"},
    ])
    assert r["latest"] == "2.0"
    assert r["total"] == 2
