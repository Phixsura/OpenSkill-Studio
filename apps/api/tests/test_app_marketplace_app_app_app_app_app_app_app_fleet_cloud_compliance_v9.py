from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_compliance_v9 import fleet_cloud_compliance_v9
def test_cc4_v9():
    r = fleet_cloud_compliance_v9([{"passed": 100, "failed": 0}])
    assert r["compliance_score"] == 100.0
    assert r["healthy"]
