from app.services.app_marketplace_app_app_app_app_app_app_app_inc_timeline import build_timeline, time_to_resolve

def test_timeline():
    r = build_timeline([
        {"type": "alert", "timestamp": 1000},
        {"type": "ack", "timestamp": 1060},
        {"type": "resolved", "timestamp": 1600},
    ])
    assert r["event_count"] == 3
    assert r["duration_min"] == 10.0

def test_ttr():
    r = time_to_resolve([
        {"created_at": 1000, "resolved_at": 1600},
        {"created_at": 2000, "resolved_at": 3800},
    ])
    assert r["count"] == 2
    assert r["avg_min"] == 20.0
