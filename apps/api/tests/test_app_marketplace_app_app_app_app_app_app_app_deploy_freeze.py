from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_freeze import (
    create_freeze, is_frozen, cancel_freeze, clear_freezes,
)

def test_freeze():
    clear_freezes()
    now = 1000.0
    create_freeze("Holiday", now - 100, now + 3600, ["production"])
    r = is_frozen("production", now=now)
    assert r["frozen"]
    assert r["reason"] == "Holiday"
    r2 = is_frozen("staging", now=now)
    assert not r2["frozen"]
    clear_freezes()

def test_cancel():
    clear_freezes()
    f = create_freeze("Test", 0, 99999)
    cancel_freeze(f["id"])
    assert not is_frozen(now=50)["frozen"]
    clear_freezes()
