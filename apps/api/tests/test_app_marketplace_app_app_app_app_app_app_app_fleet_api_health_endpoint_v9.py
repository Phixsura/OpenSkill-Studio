from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_health_endpoint_v9 import fleet_api_health_endpoint_v9
def test_ahe_v9():
    r = fleet_api_health_endpoint_v9([{"health_endpoint": True, "readiness_endpoint": True, "liveness_endpoint": True}])
    assert r["health"] == 1
    assert r["healthy"]
