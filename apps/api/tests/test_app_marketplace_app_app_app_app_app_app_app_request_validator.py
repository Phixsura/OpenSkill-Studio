from app.services.app_marketplace_app_app_app_app_app_app_app_request_validator import validate_request

def test_valid():
    schema = {"required": ["name", "email"], "properties": {
        "name": {"type": "string", "min_length": 1, "max_length": 100},
        "email": {"type": "string"}, "role": {"type": "string", "enum": ["admin", "member"]}}}
    r = validate_request({"name": "Alice", "email": "a@b.com", "role": "admin"}, schema)
    assert r["valid"]

def test_invalid():
    schema = {"required": ["name"], "properties": {
        "name": {"type": "string", "min_length": 2}, "age": {"type": "integer"}}}
    r = validate_request({"age": "not_int"}, schema)
    assert not r["valid"]
    assert r["error_count"] == 2  # missing name + wrong type age
