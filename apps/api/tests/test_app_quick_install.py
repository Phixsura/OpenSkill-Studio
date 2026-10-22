from app.services.app_quick_install import can_quick_install

def test_quick():
    r = can_quick_install(app={"name": "X"}, has_config_schema=False, new_permissions=[])
    assert r["quick_install"] is True
    assert r["steps_required"] == 1

def test_needs_config():
    r = can_quick_install(app={}, has_config_schema=True, new_permissions=[])
    assert r["quick_install"] is False
    assert r["needs_config"] is True

def test_needs_consent():
    r = can_quick_install(app={}, has_config_schema=False, new_permissions=["write:cohorts"])
    assert r["quick_install"] is False
    assert r["steps_required"] == 2
