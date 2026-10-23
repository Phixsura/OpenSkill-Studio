from app.services.app_marketplace_app_app_app_app_app_app_app_req_validator import validate_fields

def test_valid():
    rules = [
        {"field": "name", "type": "string", "required": True, "min_length": 2},
        {"field": "email", "type": "email", "required": True},
    ]
    r = validate_fields({"name": "Alice", "email": "alice@test.com"}, rules)
    assert r["valid"]

def test_errors():
    rules = [
        {"field": "name", "type": "string", "required": True},
        {"field": "email", "type": "email", "required": True},
        {"field": "url", "type": "url"},
    ]
    r = validate_fields({"email": "bad", "url": "not-a-url"}, rules)
    assert not r["valid"]
    assert r["error_count"] == 3  # name missing, email invalid, url invalid
