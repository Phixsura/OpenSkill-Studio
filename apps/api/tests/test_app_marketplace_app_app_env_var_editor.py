from app.services.app_marketplace_app_app_env_var_editor import validate_env_var, build_env_list

def test_valid_key():
    r = validate_env_var(key="DATABASE_URL", value="postgres://localhost")
    assert r["valid"]
    assert r["is_sensitive"] is False

def test_sensitive():
    r = validate_env_var(key="API_KEY", value="sk-123")
    assert r["is_sensitive"]

def test_invalid_key():
    r = validate_env_var(key="bad key!", value="v")
    assert not r["valid"]

def test_masking():
    vars_ = [{"key": "SECRET_TOKEN", "value": "super_secret_value_123"}]
    r = build_env_list(variables=vars_)
    assert "•" in r["variables"][0]["value"]
    assert r["sensitive_count"] == 1
