from app.services.app_marketplace_app_dynamic_config import create_config_entry, get_config_snapshot

def test_string():
    r = create_config_entry(key="APP_NAME", value="MyApp")
    assert r["value"] == "MyApp"
    assert r["value_type"] == "string"

def test_number():
    r = create_config_entry(key="MAX_RETRIES", value="3", value_type="number")
    assert r["value"] == 3.0

def test_boolean():
    r = create_config_entry(key="DEBUG", value="true", value_type="boolean")
    assert r["value"] is True

def test_invalid_number():
    r = create_config_entry(key="X", value="abc", value_type="number")
    assert "error" in r

def test_snapshot():
    configs = [
        {"key": "A", "value": "1", "environment": "all"},
        {"key": "B", "value": "2", "environment": "production"},
        {"key": "C", "value": "3", "environment": "staging"},
    ]
    r = get_config_snapshot(configs=configs, environment="production")
    assert r["total_keys"] == 2
    assert "C" not in r["config"]
