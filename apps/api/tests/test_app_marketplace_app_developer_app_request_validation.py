from app.services.app_marketplace_app_developer_app_request_validation import validate_request, build_validation_schema

def test_valid():
    schema = {"fields": {"name": {"type": "string", "required": True}, "age": {"type": "integer"}}}
    r = validate_request(body={"name": "Alice", "age": 30}, schema=schema)
    assert r["valid"]

def test_missing_required():
    schema = {"fields": {"name": {"type": "string", "required": True}}}
    r = validate_request(body={}, schema=schema)
    assert not r["valid"]
    assert r["errors"][0]["error"] == "required"

def test_wrong_type():
    schema = {"fields": {"age": {"type": "integer"}}}
    r = validate_request(body={"age": "not a number"}, schema=schema)
    assert not r["valid"]

def test_email():
    schema = {"fields": {"email": {"type": "email"}}}
    assert validate_request(body={"email": "a@b.com"}, schema=schema)["valid"]
    assert not validate_request(body={"email": "invalid"}, schema=schema)["valid"]

def test_min_length():
    schema = {"fields": {"name": {"type": "string", "min_length": 3}}}
    assert not validate_request(body={"name": "ab"}, schema=schema)["valid"]

def test_build():
    s = build_validation_schema(fields=[{"name": "email", "type": "email", "required": True}])
    assert s["field_count"] == 1
    assert s["fields"]["email"]["required"]
