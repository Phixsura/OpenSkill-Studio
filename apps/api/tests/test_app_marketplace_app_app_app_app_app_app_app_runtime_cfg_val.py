from app.services.app_marketplace_app_app_app_app_app_app_app_runtime_cfg_val import validate_runtime_config

def test_valid():
    r = validate_runtime_config(
        {"port": 8080, "host": "0.0.0.0", "debug": False},
        {"port": {"type": "int", "required": True},
         "host": {"type": "str", "required": True, "pattern": r"^\d+\.\d+\.\d+\.\d+$"},
         "debug": {"type": "bool"}})
    assert r["valid"]

def test_errors():
    r = validate_runtime_config(
        {"port": "not_int"},
        {"port": {"type": "int", "required": True}, "host": {"type": "str", "required": True}})
    assert not r["valid"]
    assert len(r["errors"]) == 2  # wrong type + missing host
