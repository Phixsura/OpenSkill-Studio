from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_health_score_v9 import fleet_api_health_score_v9
def test_ahs_v9():
    r = fleet_api_health_score_v9([{"health_score": 98}, {"health_score": 95}])
    assert r["avg_health_score"] == 96.5
    assert r["healthy"]
