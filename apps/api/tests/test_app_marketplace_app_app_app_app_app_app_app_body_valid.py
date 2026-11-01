from app.services.app_marketplace_app_app_app_app_app_app_app_body_valid import validate_body

def test_valid():
    r = validate_body(
        {"name": "Alice", "age": 30, "tags": ["admin"]},
        {"required": ["name"], "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "number", "minimum": 0},
            "tags": {"type": "array"}}})
    assert r["valid"]

def test_invalid():
    r = validate_body(
        {"name": "", "age": -1},
        {"required": ["name", "email"], "properties": {
            "name": {"type": "string", "minLength": 1},
            "email": {"type": "string"},
            "age": {"type": "number", "minimum": 0}}})
    assert not r["valid"]
    assert len(r["errors"]) == 3  # minLength, required email, minimum age
