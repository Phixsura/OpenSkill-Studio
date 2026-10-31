from app.services.app_marketplace_app_insights import generate_app_insights

def test_growth():
    insights = generate_app_insights(
        app={"name": "App"}, analytics={"installs_30d": 500, "installs_prev_30d": 200},
        reviews={"avg_rating": 4.5, "count": 50, "reply_rate": 90}, health={"grade": "A"})
    assert any(i["title"] == "Install Growth" for i in insights)

def test_issues():
    insights = generate_app_insights(
        app={"name": "App"}, analytics={"installs_30d": 50, "installs_prev_30d": 200, "api_usage_pct": 95},
        reviews={"avg_rating": 2.5, "count": 20, "reply_rate": 30}, health={"grade": "F"})
    assert len(insights) >= 4
    assert insights[0]["priority"] == 0  # health critical first

def test_all_good():
    insights = generate_app_insights(
        app={"name": "App"}, analytics={}, reviews={"avg_rating": 4.5, "reply_rate": 100}, health={"grade": "A"})
    assert insights[0]["title"] == "Looking Good!"
