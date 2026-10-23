from app.services.app_marketplace_app_app_app_app_app_app_app_trending_algo import compute_trending_score, rank_trending

def test_score():
    s = compute_trending_score(recent_installs=1000, recent_reviews=50,
                                recent_api_calls=100000, rating=4.5, days_since_update=2)
    assert s > 0

def test_rank():
    apps = [
        {"name": "Hot App", "recent_installs": 5000, "recent_reviews": 100, "recent_api_calls": 500000, "rating": 4.8, "days_since_update": 1},
        {"name": "Cold App", "recent_installs": 10, "recent_reviews": 1, "recent_api_calls": 100, "rating": 3.0, "days_since_update": 30},
        {"name": "Medium App", "recent_installs": 500, "recent_reviews": 20, "recent_api_calls": 50000, "rating": 4.2, "days_since_update": 5},
    ]
    ranked = rank_trending(apps)
    assert ranked[0]["name"] == "Hot App"
    assert ranked[0]["rank"] == 1
    assert ranked[-1]["name"] == "Cold App"
