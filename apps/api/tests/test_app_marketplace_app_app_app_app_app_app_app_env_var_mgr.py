from app.services.app_marketplace_app_app_app_app_app_app_app_env_var_mgr import (
    set_env_var, get_env_vars, delete_env_var, validate_env,
)

def test_set_and_get():
    store = {}
    set_env_var(store, "APP_NAME", "myapp")
    set_env_var(store, "API_SECRET", "s3cret")
    vs = get_env_vars(store)
    assert vs[0]["key"] == "API_SECRET"
    assert vs[0]["value"] == "••••••••"  # auto-masked
    assert vs[1]["value"] == "myapp"  # not secret

def test_validate():
    store = {}
    set_env_var(store, "DB_HOST", "localhost")
    r = validate_env(store, ["DB_HOST", "DB_PORT"])
    assert not r["valid"]
    assert "DB_PORT" in r["missing"]

def test_invalid_key():
    r = set_env_var({}, "bad-key", "val")
    assert not r["set"]
