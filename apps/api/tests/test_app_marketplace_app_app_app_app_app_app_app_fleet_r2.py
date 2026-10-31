from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_r2 import fleet_r2_status
def test_r2():
    r = fleet_r2_status([{"objects": 10000000, "storage_gb": 500, "requests_24h": 20000000}])
    assert r["objects"] == 10000000
    assert r["in_use"]
