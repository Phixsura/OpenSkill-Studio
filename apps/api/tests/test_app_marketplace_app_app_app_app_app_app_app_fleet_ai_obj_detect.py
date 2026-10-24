from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_obj_detect import fleet_ai_object_detection
def test_od():
    r = fleet_ai_object_detection([{"active": True, "frames_24h": 50000000, "objects": 500000000, "map": 92}])
    assert r["objects"] == 500000000
    assert r["accurate"]
