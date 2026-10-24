from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_container_image_v9 import fleet_container_image_v9
def test_cimg_v9():
    r = fleet_container_image_v9([{"on_latest": True, "scanned": True, "size_mb": 256}])
    assert r["scanned"] == 1
    assert r["healthy"]
