from app.services.app_marketplace_developer_badge import evaluate_badges

def test_new_dev():
    r = evaluate_badges(developer={"app_count": 1, "total_installs": 50})
    assert r["total_earned"] == 1
    assert r["badges"][0]["id"] == "first_app"

def test_veteran():
    r = evaluate_badges(developer={"app_count": 12, "total_installs": 5000,
        "avg_rating": 4.7, "years_active": 3, "lifetime_revenue": 150000})
    assert r["total_earned"] >= 5
    assert r["highest_tier"] == "platinum"

def test_empty():
    r = evaluate_badges(developer={})
    assert r["total_earned"] == 0
    assert r["highest_tier"] is None
