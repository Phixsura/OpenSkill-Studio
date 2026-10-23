from app.services.app_marketplace_developer_leaderboard import build_leaderboard

def test_leaderboard():
    devs = [
        {"id": "d1", "name": "Alice", "installs": 5000, "revenue": 10000},
        {"id": "d2", "name": "Bob", "installs": 8000, "revenue": 5000},
        {"id": "d3", "name": "Carol", "installs": 3000, "revenue": 15000},
    ]
    r = build_leaderboard(developers=devs, metric="installs", limit=2)
    assert r["entries"][0]["display_name"] == "Bob"
    assert r["entries"][0]["rank"] == 1
    assert len(r["entries"]) == 2

def test_revenue():
    devs = [{"id": "d1", "name": "A", "revenue": 100}, {"id": "d2", "name": "B", "revenue": 500}]
    r = build_leaderboard(developers=devs, metric="revenue")
    assert r["entries"][0]["display_name"] == "B"

def test_invalid_metric():
    r = build_leaderboard(developers=[], metric="followers")
    assert "error" in r
