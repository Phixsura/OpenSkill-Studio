from app.services.app_marketplace_app_app_app_app_app_app_app_key_reminder import check_key_expiry, build_reminder_message

def test_expiry():
    r = check_key_expiry([
        {"name": "prod", "days_until_expiry": 30},
        {"name": "staging", "days_until_expiry": 5},
        {"name": "old", "days_until_expiry": -2},
    ])
    assert r["expired_count"] == 1
    assert r["expiring_count"] == 1
    assert r["needs_action"]

def test_message():
    r = check_key_expiry([{"name": "a", "days_until_expiry": -1}, {"name": "b", "days_until_expiry": 3}])
    msg = build_reminder_message(r)
    assert "expired" in msg
    assert "expiring" in msg
    assert "rotate" in msg
