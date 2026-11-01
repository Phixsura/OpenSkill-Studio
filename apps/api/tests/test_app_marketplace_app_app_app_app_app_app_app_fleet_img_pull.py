from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_img_pull import fleet_image_pull
def test_pull():
    r = fleet_image_pull([{"pull_ms": 5000, "status": "ok"}, {"pull_ms": 45000, "status": "ok"}, {"pull_ms": 0, "status": "failed"}])
    assert r["slow_pulls"] == 1
    assert r["failed"] == 1
    assert not r["healthy"]
