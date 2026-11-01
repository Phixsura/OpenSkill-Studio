from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_compliance_check_v9 import fleet_api_compliance_check_v9
def test_acc2_v9():
    r = fleet_api_compliance_check_v9([{"passed": True, "framework": "GDPR"}])
    assert r["passed"] == 1
    assert r["healthy"]
