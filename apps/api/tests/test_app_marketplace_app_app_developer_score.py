from app.services.app_marketplace_app_app_developer_score import calculate_developer_score

def test_high():
    activity = {"apps_published": 3, "total_installs": 5000, "avg_rating": 4.8,
                "reviews_responded": 20, "docs_quality": 5, "security_clean": 3, "active_days_30": 25}
    r = calculate_developer_score(activity=activity)
    assert r["tier"] in ("expert", "legend")
    assert r["score"] > 400

def test_newcomer():
    r = calculate_developer_score(activity={"apps_published": 0, "active_days_30": 2})
    assert r["tier"] == "newcomer"
    assert r["score"] < 100
