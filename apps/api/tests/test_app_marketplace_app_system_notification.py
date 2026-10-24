from app.services.app_marketplace_app_system_notification import create_system_notification, get_active_notifications

def test_create():
    r = create_system_notification(title="Planned maintenance", message="DB upgrade tonight", severity="maintenance")
    assert r["notification_id"].startswith("sys_")
    assert r["active"]

def test_invalid():
    r = create_system_notification(title="X", message="Y", severity="panic")
    assert "error" in r

def test_active():
    notifs = [
        {"severity": "info", "active": True, "expires_at": "2099-01-01T00:00:00"},
        {"severity": "critical", "active": True, "expires_at": "2099-01-01T00:00:00"},
        {"severity": "info", "active": False, "expires_at": "2099-01-01T00:00:00"},
    ]
    r = get_active_notifications(notifications=notifs)
    assert r["count"] == 2
    assert r["has_critical"]
    assert r["notifications"][0]["severity"] == "critical"  # sorted by severity
