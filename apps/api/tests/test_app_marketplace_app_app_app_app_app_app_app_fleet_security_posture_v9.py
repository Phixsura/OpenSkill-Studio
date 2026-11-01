from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_security_posture_v9 import fleet_security_posture_v9
def test_sec_v9():
    r = fleet_security_posture_v9([{"score": 95, "critical": 0, "high": 1}])
    assert r["avg_score"] == 95.0
    assert r["critical"] == 0
    assert r["healthy"]
