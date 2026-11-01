from app.services.app_marketplace_app_app_app_app_app_app_app_event_timeline import build_event_timeline

def test_timeline():
    events = [
        {"id": "1", "type": "created", "title": "App created", "timestamp": "2026-10-24T10:00:00Z", "actor": "alice"},
        {"id": "2", "type": "deployed", "title": "v2.0 deployed", "timestamp": "2026-10-24T12:00:00Z", "actor": "bob"},
        {"id": "3", "type": "error", "title": "API error", "timestamp": "2026-10-23T08:00:00Z", "actor": "system"},
    ]
    r = build_event_timeline(events)
    assert r["total"] == 3
    assert r["items"][0]["timestamp"] > r["items"][-1]["timestamp"]
    assert r["items"][0]["icon"] == "🚀"

def test_group():
    events = [
        {"id": "1", "type": "created", "title": "A", "timestamp": "2026-10-24"},
        {"id": "2", "type": "created", "title": "B", "timestamp": "2026-10-23"},
    ]
    r = build_event_timeline(events, group_by="date")
    assert r["groups"] is not None
    assert "2026-10-24" in r["groups"]
