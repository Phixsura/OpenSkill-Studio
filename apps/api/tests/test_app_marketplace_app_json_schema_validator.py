from app.services.app_marketplace_app_json_schema_validator import validate_payload

def test_valid():
    schema = {"required": ["name"], "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
    r = validate_payload(payload={"name": "Alice", "age": 30}, schema=schema)
    assert r["valid"]

def test_missing_required():
    schema = {"required": ["name", "email"], "properties": {"name": {"type": "string"}, "email": {"type": "string"}}}
    r = validate_payload(payload={"name": "Bob"}, schema=schema)
    assert not r["valid"]
    assert r["error_count"] == 1

def test_wrong_type():
    schema = {"properties": {"count": {"type": "integer"}}}
    r = validate_payload(payload={"count": "not a number"}, schema=schema)
    assert not r["valid"]

def test_min_length():
    schema = {"properties": {"name": {"type": "string", "minLength": 3}}}
    r = validate_payload(payload={"name": "AB"}, schema=schema)
    assert not r["valid"]
