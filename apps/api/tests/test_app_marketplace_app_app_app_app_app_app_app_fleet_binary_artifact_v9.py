from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_binary_artifact_v9 import fleet_binary_artifact_v9
def test_ba_v9():
    r = fleet_binary_artifact_v9([{"signed": True, "size_mb": 256, "downloads": 10000}])
    assert r["signed"] == 1
    assert r["healthy"]
