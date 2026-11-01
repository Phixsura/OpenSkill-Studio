from app.services.app_marketplace_app_app_app_app_app_app_app_popularity import compute_popularity, rank_apps_by_popularity

def test_popularity():
    r = compute_popularity(installs_30d=50000, reviews_30d=200, api_calls_30d=5000000,
                             active_users=10000, rating=4.8)
    assert r["score"] > 30
    assert r["tier"] in ("gold", "platinum")

def test_rank():
    apps = [
        {"name": "Top App", "installs_30d": 100000, "reviews_30d": 500, "api_calls_30d": 10000000, "active_users": 50000, "rating": 4.9},
        {"name": "Small App", "installs_30d": 100, "reviews_30d": 5, "api_calls_30d": 1000, "active_users": 50, "rating": 3.5},
    ]
    r = rank_apps_by_popularity(apps)
    assert r[0]["name"] == "Top App"
    assert r[0]["rank"] == 1
