from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_scorecard import fleet_scorecard
def test_sc():
    r = fleet_scorecard({"reliability": 95, "security": 90, "velocity": 85, "quality": 92})
    assert r["avg_score"] == 90.5
    assert r["grade"] == "A"
    assert r["top"] == "reliability"
    assert r["bottom"] == "velocity"
