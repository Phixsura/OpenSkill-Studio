from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_obj_store import fleet_ai_object_storage
def test_os():
    r = fleet_ai_object_storage([{"active": True, "objects": 100000000, "size_tb": 500, "ops_24h": 50000000}])
    assert r["size_tb"] == 500
    assert r["scalable"]
