from app.services.app_marketplace_app_app_app_app_app_app_app_json_schema import validate_schema

def test_valid():
    schema = {"required": ["name", "email"], "properties": {
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string"},
        "role": {"type": "string", "enum": ["admin", "user"]}}}
    r = validate_schema({"name": "Alice", "email": "a@b.com", "role": "admin"}, schema)
    assert r["valid"]

def test_invalid():
    schema = {"required": ["name"], "properties": {
        "name": {"type": "string", "minLength": 2},
        "age": {"type": "integer"}}}
    r = validate_schema({"age": "not_int"}, schema)
    assert not r["valid"]
    assert r["error_count"] >= 2

def test_nested():
    schema = {"properties": {"address": {"type": "object", "required": ["city"],
              "properties": {"city": {"type": "string"}}}}}
    r = validate_schema({"address": {}}, schema)
    assert not r["valid"]
    assert any("city" in e["path"] for e in r["errors"])
