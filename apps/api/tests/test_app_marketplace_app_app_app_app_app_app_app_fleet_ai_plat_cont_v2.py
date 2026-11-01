from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_cont_v2 import fleet_ai_container_v2
def test_cv2():
    r = fleet_ai_container_v2([{"active": True, "containers": 5000, "images": 500, "registries": 10}])
    assert r["containers"] == 5000
    assert r["containerized"]
