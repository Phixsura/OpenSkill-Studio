from app.services.app_marketplace_app_app_app_app_app_app_app_notif_center import (
    send_notification, get_notifications, mark_read, clear_notifications,
)

def test_send_get():
    clear_notifications()
    send_notification("alice", "Deploy Done", "v2.0 deployed", "deploy")
    send_notification("alice", "Alert", "CPU high", "alert", "high")
    send_notification("bob", "Welcome", "Hello!", "system")
    r = get_notifications("alice")
    assert r["total"] == 2
    assert r["unread"] == 2
    mark_read(1)
    r2 = get_notifications("alice", unread_only=True)
    assert r2["total"] == 1
    clear_notifications()
