from app.services.app_marketplace_app_app_usage_analytics import build_usage_summary, build_funnel

def test_summary():
    events = [
        {"action": "view", "user_id": "u1"},
        {"action": "click", "user_id": "u1"},
        {"action": "view", "user_id": "u2"},
    ]
    r = build_usage_summary(events=events, period="7d")
    assert r["total_events"] == 3
    assert r["unique_users"] == 2
    assert r["top_actions"][0]["action"] == "view"

def test_funnel():
    steps = [
        {"name": "Visit Page", "count": 1000},
        {"name": "Click Install", "count": 300},
        {"name": "Complete Setup", "count": 150},
    ]
    r = build_funnel(steps=steps)
    assert r["total_steps"] == 3
    assert r["overall_conversion_pct"] == 15.0
    assert r["steps"][1]["drop_off_pct"] == 70.0
