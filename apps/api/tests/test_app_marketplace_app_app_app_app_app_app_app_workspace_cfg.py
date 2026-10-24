from app.services.app_marketplace_app_app_app_app_app_app_app_workspace_cfg import get_settings, update_setting, reset_to_defaults

def test_get():
    r = get_settings({"theme": "dark", "language": "ja"})
    assert r["settings"]["theme"] == "dark"
    assert r["settings"]["timezone"] == "UTC"  # default
    assert r["customized"] == 2

def test_update():
    current = {"theme": "light"}
    r = update_setting(current, "theme", "dark")
    assert r["updated"]
    assert r["old_value"] == "light"
    r2 = update_setting(current, "invalid_key", "x")
    assert not r2["updated"]

def test_reset():
    r = reset_to_defaults()
    assert r["settings"]["theme"] == "system"
    assert r["reset"]
