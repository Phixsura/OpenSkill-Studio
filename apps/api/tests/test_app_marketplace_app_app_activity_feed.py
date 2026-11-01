from app.services.app_marketplace_app_app_activity_feed import build_activity_feed

def test_feed():
    acts = [
        {"id": "1", "actor": "Alice", "verb": "install", "target": "MyApp", "timestamp": "2026-01-02T00:00:00Z"},
        {"id": "2", "actor": "Bob", "verb": "review", "target": "MyApp", "timestamp": "2026-01-01T00:00:00Z"},
    ]
    r = build_activity_feed(activities=acts)
    assert r["count"] == 2
    assert r["activities"][0]["verb"] == "installed"
    assert not r["has_more"]

def test_limit():
    acts = [{"id": str(i), "actor": "U", "verb": "update", "target": "X"} for i in range(25)]
    r = build_activity_feed(activities=acts, limit=10)
    assert r["count"] == 10
    assert r["has_more"]
