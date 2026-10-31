from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_reliability_score_v9 import fleet_api_reliability_score_v9
def test_ars2_v9():
    r = fleet_api_reliability_score_v9([{"reliability_score": 99.99, "incidents_30d": 0}])
    assert r["avg_reliability"] == 99.99
    assert r["healthy"]
