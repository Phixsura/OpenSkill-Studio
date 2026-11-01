from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_health_score import fleet_health_score
def test_score():
    r = fleet_health_score([{"health_score": 95}, {"health_score": 85}, {"health_score": 90}])
    assert r["score"] == 90
    assert r["grade"] == "A"
