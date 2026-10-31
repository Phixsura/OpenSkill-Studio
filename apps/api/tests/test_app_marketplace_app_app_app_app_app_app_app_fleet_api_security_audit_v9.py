from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_security_audit_v9 import fleet_api_security_audit_v9
def test_asa2_v9():
    r = fleet_api_security_audit_v9([{"completed": True, "findings": 5, "fixed": 5}])
    assert r["findings"] == r["fixed"]
    assert r["healthy"]
