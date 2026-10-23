from app.services.app_marketplace_app_environment_config import validate_env_key, set_env_var, list_env_vars

def test_valid_key():
    assert validate_env_key(key="MY_VAR")["valid"]

def test_invalid_key():
    assert not validate_env_key(key="my-var")["valid"]
    assert not validate_env_key(key="123ABC")["valid"]

def test_set():
    r = set_env_var(app_id="a1", key="API_KEY", value="secret123", is_secret=True)
    assert r["success"]
    assert r["display_value"] == "••••••••"
    assert r["encryption_key_id"] is not None

def test_set_plain():
    r = set_env_var(app_id="a1", key="LOG_LEVEL", value="debug", is_secret=False)
    assert r["display_value"] == "debug"

def test_list():
    r = list_env_vars(app_id="a1")
    assert r["total"] == 3
    assert r["secret_count"] == 1
