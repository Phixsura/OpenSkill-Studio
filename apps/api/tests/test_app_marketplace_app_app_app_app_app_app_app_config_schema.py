from app.services.app_marketplace_app_app_app_app_app_app_app_config_schema import validate_config

def test_valid():
    schema = [
        {"key": "name", "type": "string", "required": True},
        {"key": "port", "type": "number", "min": 1, "max": 65535},
    ]
    r = validate_config(schema, {"name": "app", "port": 8080})
    assert r["valid"]
    assert r["error_count"] == 0

def test_errors():
    schema = [
        {"key": "name", "type": "string", "required": True},
        {"key": "mode", "type": "string", "enum": ["dev", "prod"]},
    ]
    r = validate_config(schema, {"mode": "test", "extra": 1})
    assert not r["valid"]
    assert r["error_count"] == 2  # missing name + invalid enum
    assert r["warning_count"] == 1  # extra unknown field
