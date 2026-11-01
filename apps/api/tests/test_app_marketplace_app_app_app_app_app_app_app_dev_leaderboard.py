from app.services.app_marketplace_app_app_app_app_app_app_app_dev_leaderboard import build_leaderboard

def test_leaderboard():
    r = build_leaderboard([
        {"developer": "alice", "commits": 50, "prs": 10, "reviews": 20},
        {"developer": "bob", "commits": 30, "prs": 15, "reviews": 5},
        {"developer": "carol", "commits": 80, "prs": 5, "reviews": 10},
    ])
    assert r["total_developers"] == 3
    assert r["leaderboard"][0]["developer"] in ("alice", "carol")  # top scorer
    assert r["leaderboard"][0]["rank"] == 1
