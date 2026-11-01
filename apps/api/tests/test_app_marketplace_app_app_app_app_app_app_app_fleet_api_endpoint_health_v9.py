from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_endpoint_health_v9 import fleet_api_endpoint_health_v9
def test_aeph_v9():
    r = fleet_api_endpoint_health_v9([{"health_score": 98}])
    assert r["healthy"] == 1
    assert r["all_healthy"]
