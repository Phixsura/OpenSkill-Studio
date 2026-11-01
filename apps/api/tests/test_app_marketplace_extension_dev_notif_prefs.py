from app.services.app_marketplace_extension_dev_notif_prefs import DevNotifPrefsService

def test_defaults():
    svc = DevNotifPrefsService()
    p = svc.get_or_create("u1")
    assert p.channels["email"] is True
    assert p.channels["webhook"] is False

def test_set_channel():
    svc = DevNotifPrefsService()
    svc.set_channel("u1", "webhook", True)
    assert svc.get_or_create("u1").channels["webhook"] is True

def test_should_notify():
    svc = DevNotifPrefsService()
    assert svc.should_notify("u1", "install", "email") is True
    assert svc.should_notify("u1", "install", "webhook") is False

def test_quiet_hours():
    svc = DevNotifPrefsService()
    svc.set_quiet_hours("u1", 22, 6)
    assert svc.should_notify("u1", "install", "email", hour=23) is False
    assert svc.should_notify("u1", "install", "email", hour=12) is True
