from app.services.app_marketplace_app_app_timeline import build_timeline

def test_timeline():
    events = [
        {"id": "1", "title": "Published", "timestamp": "2026-01-02T00:00:00Z", "icon": "🚀"},
        {"id": "2", "title": "Created", "timestamp": "2026-01-01T00:00:00Z", "icon": "✨"},
    ]
    r = build_timeline(events=events)
    assert r["count"] == 2
    assert r["items"][0]["title"] == "Published"  # newest first

def test_xss():
    r = build_timeline(events=[{"title": "<b>XSS</b>", "actor": "<script>"}])
    assert "<b>" not in r["items"][0]["title"]
    assert "<script>" not in r["items"][0]["actor"]
