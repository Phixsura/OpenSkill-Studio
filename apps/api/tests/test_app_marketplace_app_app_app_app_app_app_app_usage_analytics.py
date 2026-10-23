from app.services.app_marketplace_app_app_app_app_app_app_app_usage_analytics import aggregate_usage

def test_aggregate():
    events = [
        {"action": "view", "date": "2024-01-01", "user_id": "u1"},
        {"action": "click", "date": "2024-01-01", "user_id": "u1"},
        {"action": "view", "date": "2024-01-02", "user_id": "u2"},
        {"action": "view", "date": "2024-01-02", "user_id": "u3"},
    ]
    r = aggregate_usage(events)
    assert r["total_events"] == 4
    assert r["unique_users"] == 3
    assert r["top_action"] == "view"
    assert r["by_action"]["view"] == 3
    assert r["avg_per_day"] == 2.0

def test_empty():
    r = aggregate_usage([])
    assert r["total_events"] == 0
    assert r["unique_users"] == 0
