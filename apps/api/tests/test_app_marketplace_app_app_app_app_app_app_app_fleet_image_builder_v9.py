from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_image_builder_v9 import fleet_image_builder_v9
def test_ib_v9():
    r = fleet_image_builder_v9([{"status": "success", "build_time_sec": 60}, {"status": "success", "build_time_sec": 45}])
    assert r["success"] == 2
    assert r["avg_build_time_sec"] == 52.5
    assert r["healthy"]
