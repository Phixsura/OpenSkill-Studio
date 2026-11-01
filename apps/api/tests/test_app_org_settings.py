from app.services.app_org_settings import get_settings, update_settings

def test_defaults():
    s = get_settings("new-org")
    assert s["auto_upgrade_apps"] is True
    assert s["max_apps_per_org"] == 50

def test_update():
    s = update_settings("org-1", {"max_apps_per_org": 100})
    assert s["max_apps_per_org"] == 100
    assert s["auto_upgrade_apps"] is True  # unchanged

def test_ignore_unknown():
    s = update_settings("org-2", {"unknown_field": True})
    assert "unknown_field" not in s
