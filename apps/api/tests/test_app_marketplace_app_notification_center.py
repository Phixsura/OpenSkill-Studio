from app.services.app_marketplace_app_notification_center import create_notification, get_notification_summary

def test_create():
    r = create_notification(user_id="u1", title="Deploy success", message="v2.0 deployed",
                             ntype="success", action_url="/deploys/123")
    assert r["notification_id"].startswith("notif_")
    assert r["icon"] == "✅"
    assert not r["read"]

def test_summary():
    notifs = [
        {"type": "info", "read": True},
        {"type": "warning", "read": False},
        {"type": "action_required", "read": False},
    ]
    r = get_notification_summary(notifications=notifs)
    assert r["unread"] == 2
    assert r["action_required"] == 1
    assert r["by_type"]["warning"] == 1
