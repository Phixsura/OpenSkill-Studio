from app.services.app_marketplace_app_app_app_app_app_app_app_compat_check import check_compatibility, version_compatibility_matrix

def test_compatible():
    r = check_compatibility(
        {"fields": {"name": "string", "age": "int"}},
        {"fields": {"name": "string", "age": "int", "bio": "string"}})
    assert r["compatible"]

def test_breaking():
    r = check_compatibility(
        {"fields": {"name": "string", "age": "int"}, "required": ["name"]},
        {"fields": {"name": "int"}, "required": ["name", "email"]})
    assert not r["compatible"]
    assert len(r["breaking"]) >= 2  # age removed + name type changed

def test_matrix():
    r = version_compatibility_matrix([
        {"version": "1.0", "schema": {"fields": {"a": "string"}}},
        {"version": "1.1", "schema": {"fields": {"a": "string", "b": "int"}}},
        {"version": "2.0", "schema": {"fields": {"a": "int"}}},
    ])
    assert r["comparisons"][0]["compatible"]  # 1.0→1.1
    assert not r["comparisons"][1]["compatible"]  # 1.1→2.0
    assert not r["all_compatible"]
