from app.services.app_marketplace_app_app_config_schema import validate_schema

def test_valid():
    fields = [
        {"name": "api_key", "type": "secret", "required": True, "description": "Your API key"},
        {"name": "region", "type": "select", "options": ["us", "eu", "ap"]},
        {"name": "debug", "type": "boolean", "default": False},
    ]
    r = validate_schema(fields=fields)
    assert r["valid"]
    assert r["field_count"] == 3
    assert r["required_count"] == 1

def test_duplicate():
    r = validate_schema(fields=[{"name": "x", "type": "string"}, {"name": "x", "type": "string"}])
    assert not r["valid"]
    assert "Duplicate" in r["errors"][0]

def test_bad_type():
    r = validate_schema(fields=[{"name": "x", "type": "unknown_type"}])
    assert not r["valid"]
