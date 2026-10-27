from app.services.app_marketplace_extension_user_prefs import ExtUserPrefsService

def test_defaults():
    svc = ExtUserPrefsService()
    p = svc.get("u1")
    assert p.theme == "system"
    assert p.auto_update is True

def test_update():
    svc = ExtUserPrefsService()
    ok, _ = svc.update("u1", theme="dark", show_beta=True)
    assert ok is True
    assert svc.get("u1").theme == "dark"

def test_invalid():
    svc = ExtUserPrefsService()
    ok, errors = svc.update("u1", theme="rainbow")
    assert ok is False

def test_reset():
    svc = ExtUserPrefsService()
    svc.update("u1", theme="dark")
    svc.reset("u1")
    assert svc.get("u1").theme == "system"
