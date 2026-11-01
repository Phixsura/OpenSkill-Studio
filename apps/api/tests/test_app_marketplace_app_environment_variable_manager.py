from app.services.app_marketplace_app_environment_variable_manager import is_sensitive, mask_value, set_env_var, list_env_vars

def test_sensitive():
    assert is_sensitive("API_KEY")
    assert is_sensitive("db_password")
    assert not is_sensitive("APP_NAME")

def test_mask():
    assert mask_value("mysecretvalue") == "my*********ue"
    assert mask_value("ab") == "****"

def test_set():
    r = set_env_var(app_id="a1", key="DATABASE_URL", value="postgres://localhost")
    assert r["error"] is None

def test_set_invalid():
    r = set_env_var(app_id="a1", key="bad-key", value="x")
    assert r["error"]

def test_list():
    vars = [{"key": "API_KEY", "value": "secret123"}, {"key": "APP_NAME", "value": "MyApp"}]
    r = list_env_vars(vars=vars)
    assert "****" in r[0]["value"]  # masked
    assert r[1]["value"] == "MyApp"  # not masked
