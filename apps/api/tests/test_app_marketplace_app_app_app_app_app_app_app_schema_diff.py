from app.services.app_marketplace_app_app_app_app_app_app_app_schema_diff import diff_schemas, schema_compatibility

def test_diff():
    r = diff_schemas(["id", "name", "email"], ["id", "name", "avatar", "role"])
    assert r["added"] == ["avatar", "role"]
    assert r["removed"] == ["email"]
    assert r["breaking"]
    assert r["total_changes"] == 3

def test_compat():
    diffs = [diff_schemas(["a"], ["a", "b"]), diff_schemas(["x", "y"], ["x"])]
    r = schema_compatibility(diffs)
    assert r["total_breaking"] == 1  # second removes y
    assert not r["compatible"]
