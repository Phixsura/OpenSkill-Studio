from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_vision import fleet_ai_vision
def test_vis():
    r = fleet_ai_vision([{"active": True, "images_24h": 2000000, "detections_24h": 10000000}])
    assert r["images_24h"] == 2000000
    assert r["all_active"]
