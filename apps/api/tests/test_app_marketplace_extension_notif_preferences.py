from app.services.app_marketplace_extension_notif_preferences import ExtensionNotifPreferencesService


def test_initialize():
    svc = ExtensionNotifPreferencesService()
    prefs = svc.initialize("user-1")
    assert len(prefs) == 10
    # Critical events should have push enabled
    critical = next(p for p in prefs if p.event_type == "error.critical")
    assert critical.push is True


def test_update_preference():
    svc = ExtensionNotifPreferencesService()
    svc.initialize("user-1")
    pref = svc.update("user-1", "deploy.success", email=False, push=True)
    assert pref.email is False
    assert pref.push is True


def test_should_notify():
    svc = ExtensionNotifPreferencesService()
    svc.initialize("user-1")
    svc.update("user-1", "install.new", email=False)
    assert svc.should_notify("user-1", "install.new", "email") is False
    assert svc.should_notify("user-1", "install.new", "in_app") is True


def test_dnd():
    svc = ExtensionNotifPreferencesService()
    svc.initialize("user-1")
    svc.toggle_dnd("user-1")
    assert svc.is_dnd("user-1") is True
    assert svc.should_notify("user-1", "deploy.success", "email") is False
    svc.toggle_dnd("user-1")
    assert svc.is_dnd("user-1") is False


def test_quiet_hours():
    svc = ExtensionNotifPreferencesService()
    qh = svc.set_quiet_hours("user-1", True, start=23, end=7)
    assert qh.enabled is True
    assert qh.start_hour == 23


def test_summary():
    svc = ExtensionNotifPreferencesService()
    svc.initialize("user-1")
    svc.toggle_dnd("user-1")
    summary = svc.get_summary("user-1")
    assert summary["total_events"] == 10
    assert summary["dnd"] is True
    assert summary["email_enabled"] == 10
