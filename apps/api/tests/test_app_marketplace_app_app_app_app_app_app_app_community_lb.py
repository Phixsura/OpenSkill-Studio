from app.services.app_marketplace_app_app_app_app_app_app_app_community_lb import build_community_leaderboard

def test_leaderboard():
    r = build_community_leaderboard([
        {"name": "Alice", "forum_posts": 50, "forum_replies": 200, "bugs_reported": 10, "apps_published": 3, "reviews_written": 20},
        {"name": "Bob", "forum_posts": 30, "forum_replies": 100, "bugs_reported": 5, "apps_published": 1, "reviews_written": 10},
    ])
    assert r["total"] == 2
    assert r["top_contributor"] == "Alice"
    assert r["leaderboard"][0]["badge"] == "🥇"
    assert r["leaderboard"][0]["score"] > r["leaderboard"][1]["score"]
