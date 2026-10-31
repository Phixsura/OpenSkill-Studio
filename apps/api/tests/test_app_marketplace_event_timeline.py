from app.services.app_marketplace_event_timeline import build_timeline, group_by_date

def test_timeline():
    events = [
        {"type": "install", "timestamp": "2026-01-02T10:00:00Z", "actor": "u1"},
        {"type": "review", "timestamp": "2026-01-01T10:00:00Z", "title": "New review"},
    ]
    t = build_timeline(events=events)
    assert t["showing"] == 2
    assert t["items"][0]["type"] == "install"  # newest first
    assert t["items"][0]["icon"] == "📥"

def test_limit():
    events = [{"type": "install", "timestamp": f"2026-01-{i:02d}T00:00:00Z"} for i in range(1, 20)]
    t = build_timeline(events=events, limit=5)
    assert t["showing"] == 5
    assert t["total"] == 19

def test_group():
    items = [{"timestamp": "2026-01-01T10:00:00Z"}, {"timestamp": "2026-01-01T11:00:00Z"},
             {"timestamp": "2026-01-02T10:00:00Z"}]
    g = group_by_date(timeline_items=items)
    assert len(g["groups"]) == 2
