from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_do import fleet_durable_objects
def test_do():
    r = fleet_durable_objects([{"active_objects": 10000, "storage_mb": 500, "requests_24h": 5000000}])
    assert r["active_objects"] == 10000
    assert r["in_use"]
