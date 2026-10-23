from app.services.app_marketplace_app_app_app_app_app_app_app_dev_leaderboard import build_leaderboard

def test_leaderboard():
    devs = [
        {"name": "Alice", "commits": 50, "pull_requests": 10, "reviews": 20, "deploys": 5},
        {"name": "Bob", "commits": 80, "pull_requests": 5, "reviews": 10, "deploys": 2},
        {"name": "Carol", "commits": 30, "pull_requests": 15, "reviews": 30, "deploys": 8},
    ]
    r = build_leaderboard(devs)
    assert r["total_developers"] == 3
    assert r["leaderboard"][0]["badge"] == "🥇"
    assert r["top_contributor"] in ("Alice", "Bob", "Carol")
    assert r["leaderboard"][0]["score"] > r["leaderboard"][1]["score"]
