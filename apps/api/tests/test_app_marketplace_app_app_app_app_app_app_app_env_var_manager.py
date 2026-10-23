from app.services.app_marketplace_app_app_app_app_app_app_app_env_var_manager import (
    create_env_store, set_var, get_var, list_vars)

def test_env_vars():
    store = create_env_store()
    r = set_var(store, "DATABASE_URL", "postgres://user:pass@host/db")
    assert r["status"] == "set"
    assert "****" in r["masked"]
    g = get_var(store, "DATABASE_URL")
    assert g["status"] == "found"
    assert "****" in g["value"]
    g2 = get_var(store, "DATABASE_URL", unmask=True)
    assert g2["value"] == "postgres://user:pass@host/db"
    set_var(store, "APP_ENV", "production", sensitive=False)
    lst = list_vars(store)
    assert lst["count"] == 2
    assert lst["vars"][0]["key"] == "APP_ENV"

def test_invalid_key():
    store = create_env_store()
    r = set_var(store, "bad key!", "val")
    assert "error" in r
