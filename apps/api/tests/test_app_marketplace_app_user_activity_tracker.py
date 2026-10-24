from app.services.app_marketplace_app_user_activity_tracker import track_activity, get_activity_summary

def test_track():
    r = track_activity(user_id="u1", action="view_app", resource="app_123")
    assert r["user_id"] == "u1"
    assert r["action"] == "view_app"

def test_summary():
    activities = [
        {"user_id": "u1", "action": "view", "timestamp": "2026-10-23T12:00:00"},
        {"user_id": "u1", "action": "install", "timestamp": "2026-10-23T13:00:00"},
        {"user_id": "u2", "action": "view", "timestamp": "2026-10-22T10:00:00"},
    ]
    r = get_activity_summary(activities=activities, period_days=7)
    assert r["total_activities"] == 3
    assert r["unique_users"] == 2
    assert r["top_actions"][0]["action"] == "view"
    assert r["avg_daily"] > 0
