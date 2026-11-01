from app.services.app_marketplace_app_app_app_app_app_app_app_tenant_config import get_config, update_config, validate_config

def test_defaults():
    r = get_config("org1")
    assert r["config"]["theme"] == "light"
    assert r["config"]["features"]["analytics"]
    assert not r["has_overrides"]

def test_overrides():
    r = get_config("org1", overrides={"theme": "dark", "features": {"sandbox": True}})
    assert r["config"]["theme"] == "dark"
    assert r["config"]["features"]["sandbox"]
    assert r["config"]["features"]["analytics"]  # inherited

def test_update():
    base = {"theme": "light", "limits": {"max_apps": 10}}
    r = update_config(base, {"theme": "dark"})
    assert r["config"]["theme"] == "dark"
    assert "theme" in r["changed_keys"]

def test_validate():
    assert validate_config({"theme": "dark", "limits": {"max_apps": 5, "max_users": 10}})["valid"]
    assert not validate_config({"theme": "neon", "limits": {"max_apps": 0, "max_users": 1}})["valid"]
