from app.services.app_marketplace_app_app_app_user_engagement import build_engagement_metrics

def test_engagement():
    events = [
        {"user_id": "u1", "action": "view", "timestamp": "2026-01-01T10:00:00Z"},
        {"user_id": "u2", "action": "view", "timestamp": "2026-01-01T11:00:00Z"},
        {"user_id": "u1", "action": "click", "timestamp": "2026-01-01T12:00:00Z"},
        {"user_id": "u1", "action": "view", "timestamp": "2026-01-02T10:00:00Z"},
    ]
    r = build_engagement_metrics(events=events)
    assert r["total_events"] == 4
    assert r["avg_dau"] >= 1
    assert r["top_actions"][0]["action"] == "view"

def test_empty():
    r = build_engagement_metrics(events=[])
    assert r["total_events"] == 0
    assert r["avg_dau"] == 0
