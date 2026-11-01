from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_notif import create_notification, notification_summary

def test_notify():
    r = create_notification("d1", "3.0", "production", "alice", "success", ["slack", "email"])
    assert r["sent"]
    assert r["channels_notified"] == 2

def test_invalid():
    r = create_notification("d1", "3.0", "prod", "bob", "success", ["telegram"])
    assert not r["sent"]

def test_summary():
    notifs = [
        {"environment": "production", "deploy_status": "success"},
        {"environment": "staging", "deploy_status": "success"},
        {"environment": "production", "deploy_status": "failed"},
    ]
    r = notification_summary(notifs)
    assert r["total"] == 3
    assert r["by_environment"]["production"] == 2
