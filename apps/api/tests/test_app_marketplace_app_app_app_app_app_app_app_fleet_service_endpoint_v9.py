from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_endpoint_v9 import fleet_service_endpoint_v9
def test_sep_v9():
    r = fleet_service_endpoint_v9([{"ready": True, "addresses": 3}])
    assert r["ready"] == 1
    assert r["healthy"]
