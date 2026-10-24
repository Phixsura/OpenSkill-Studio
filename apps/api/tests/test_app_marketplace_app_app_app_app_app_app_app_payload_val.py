from app.services.app_marketplace_app_app_app_app_app_app_app_payload_val import validate_payload

def test_valid():
    r = validate_payload({"name": "Alice", "age": 30},
        {"name": {"type": "string", "required": True}, "age": {"type": "int", "min_value": 0}})
    assert r["valid"]

def test_errors():
    r = validate_payload({"age": -1},
        {"name": {"type": "string", "required": True}, "age": {"type": "int", "min_value": 0}})
    assert not r["valid"]
    assert r["error_count"] == 2  # name required + age min
