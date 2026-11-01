from app.services.app_marketplace_app_app_app_app_app_app_app_config_hotswap import (
    stage_config, activate_pending, get_active, reset_hotswap,
)

def test_hotswap():
    reset_hotswap()
    s = stage_config({"port": 8080, "debug": False})
    assert s["staged"]
    a = activate_pending()
    assert a["activated"]
    r = get_active()
    assert r["active"]
    assert r["config"]["port"] == 8080
    # Stage new config
    stage_config({"port": 9090, "debug": True})
    a2 = activate_pending()
    assert a2["previous_hash"] == s["hash"]
    assert get_active()["config"]["port"] == 9090
    reset_hotswap()

def test_no_pending():
    reset_hotswap()
    r = activate_pending()
    assert not r["activated"]
    reset_hotswap()
