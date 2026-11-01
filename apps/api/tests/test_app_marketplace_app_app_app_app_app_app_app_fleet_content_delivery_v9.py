from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_content_delivery_v9 import fleet_content_delivery_v9
def test_cd2_v9():
    r = fleet_content_delivery_v9([{"optimized": True, "compressed": True, "bandwidth_saved_gb": 100}])
    assert r["optimized"] == 1
    assert r["healthy"]
