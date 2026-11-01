from app.services.app_marketplace_app_app_app_app_app_app_app_live_config import (
    load_config, get_config, config_history, reset_config,
)

def test_load_reload():
    reset_config()
    r = load_config({"debug": False, "port": 8080})
    assert r["changed"]
    assert r["version"] == 1
    r2 = load_config({"debug": True, "port": 8080})
    assert r2["changed"]
    assert r2["version"] == 2
    c = get_config()
    assert c["config"]["debug"] is True
    h = config_history()
    assert len(h) == 2
    reset_config()

def test_no_change():
    reset_config()
    load_config({"a": 1})
    r = load_config({"a": 1})
    assert not r["changed"]
    assert r["version"] == 1
    reset_config()
