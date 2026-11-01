from app.services.app_marketplace_app_app_app_leaderboard import build_leaderboard

def test_leaderboard():
    apps = [
        {"name": "AppA", "downloads": 5000, "author": "Alice"},
        {"name": "AppB", "downloads": 15000, "author": "Bob"},
        {"name": "AppC", "downloads": 8000, "author": "Charlie"},
    ]
    r = build_leaderboard(apps=apps, metric="downloads")
    assert r["entries"][0]["name"] == "AppB"
    assert r["entries"][0]["medal"] == "🥇"
    assert r["entries"][1]["medal"] == "🥈"
    assert r["total_ranked"] == 3
