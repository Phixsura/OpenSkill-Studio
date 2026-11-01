from app.services.app_marketplace_app_app_app_app_app_app_app_config_valid import validate_config

def test_valid():
    r = validate_config(
        {"port": 8080, "host": "0.0.0.0", "debug": False},
        {"port": {"type": "int", "required": True, "min": 1, "max": 65535},
         "host": {"type": "string", "required": True},
         "debug": {"type": "bool"}})
    assert r["valid"]

def test_invalid():
    r = validate_config(
        {"port": "not_a_number"},
        {"port": {"type": "int", "required": True},
         "host": {"type": "string", "required": True}})
    assert not r["valid"]
    assert len(r["errors"]) == 2  # wrong type + missing host

def test_enum():
    r = validate_config(
        {"env": "invalid"},
        {"env": {"type": "string", "enum": ["prod", "staging", "dev"]}})
    assert not r["valid"]
