from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_posture_v9 import fleet_cloud_posture_v9
def test_cspm_v9():
    r = fleet_cloud_posture_v9([{"compliant": True, "misconfigurations": 0, "score": 95}])
    assert r["avg_score"] == 95.0
    assert r["healthy"]
