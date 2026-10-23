from app.services.app_marketplace_app_app_runtime_config import validate_config, merge_configs

SCHEMA = {
    "port": {"type": "integer", "default": 3000, "required": False},
    "debug": {"type": "boolean", "default": False},
    "name": {"type": "string", "required": True},
}

def test_valid():
    r = validate_config(schema=SCHEMA, values={"name": "MyApp", "port": 8080})
    assert r["valid"]
    assert r["config"]["port"] == 8080
    assert r["config"]["debug"] is False  # default

def test_missing_required():
    r = validate_config(schema=SCHEMA, values={})
    assert not r["valid"]

def test_wrong_type():
    r = validate_config(schema=SCHEMA, values={"name": "X", "port": "not-int"})
    assert not r["valid"]

def test_merge():
    r = merge_configs(base={"a": 1, "b": 2}, override={"b": 99, "c": 3})
    assert r["config"]["b"] == 99
    assert r["overridden_keys"] == ["b"]
