from app.services.app_developer_notification_prefs import get_prefs, update_prefs, should_notify, DEFAULT_PREFS

def test_defaults():
    p = get_prefs("new-dev")
    assert p["app_installed"] is True
    assert p["email_enabled"] is True

def test_update():
    p = update_prefs("upd-dev", {"app_installed": False})
    assert p["app_installed"] is False
    assert p["review_decided"] is True  # unchanged

def test_should_notify():
    assert should_notify("x", "app_installed") is True

def test_should_not_notify_disabled():
    update_prefs("dis-dev", {"app_installed": False})
    assert should_notify("dis-dev", "app_installed") is False

def test_should_not_notify_email_off():
    update_prefs("email-off", {"email_enabled": False})
    assert should_notify("email-off", "app_installed") is False

def test_ignore_invalid_keys():
    p = update_prefs("inv-dev", {"invalid_key": True, "app_installed": False})
    assert "invalid_key" not in p or p.get("invalid_key") is None
