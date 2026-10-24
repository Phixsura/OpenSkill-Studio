from app.services.app_marketplace_app_app_user_activity_log import build_activity_log

def test_log():
    activities = [
        {"action": "login", "target": "", "timestamp": "2026-01-01T10:00:00Z", "ip": "1.2.3.4"},
        {"action": "create_app", "target": "SuperApp", "timestamp": "2026-01-01T10:05:00Z"},
        {"action": "deploy", "target": "v2.0.0", "timestamp": "2026-01-02T09:00:00Z"},
    ]
    r = build_activity_log(activities=activities)
    assert r["total"] == 3
    assert r["activities"][0]["label"] == "Logged in"
    assert r["active_days"] == 2
