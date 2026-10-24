from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_compliance_posture_v9 import fleet_compliance_posture_v9
def test_cp2_v9():
    r = fleet_compliance_posture_v9([{"score": 95, "framework": "SOC2", "open_findings": 0}])
    assert r["avg_score"] == 95.0
    assert r["healthy"]
