from app.services.app_marketplace_app_settings_v2 import get_settings_schema, validate_setting

def test_all_groups():
    s = get_settings_schema()
    assert "general" in s["groups"]
    assert len(s["groups"]) >= 3

def test_single_group():
    s = get_settings_schema(group="security")
    assert s["group"] == "security"
    assert len(s["settings"]) == 3

def test_validate_ok():
    r = validate_setting(key="app_name", value="MyApp", schema={"type": "string", "required": True, "max_length": 50})
    assert r["valid"]

def test_validate_required():
    r = validate_setting(key="app_name", value="", schema={"type": "string", "required": True})
    assert not r["valid"]

def test_validate_max_length():
    r = validate_setting(key="name", value="x" * 100, schema={"type": "string", "max_length": 50})
    assert not r["valid"]

def test_validate_integer_range():
    r = validate_setting(key="timeout", value=3, schema={"type": "integer", "min": 5, "max": 1440})
    assert not r["valid"]
