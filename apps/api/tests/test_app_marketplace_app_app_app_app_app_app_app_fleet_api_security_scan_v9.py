from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_security_scan_v9 import fleet_api_security_scan_v9
def test_ass_v9():
    r = fleet_api_security_scan_v9([{"passed": True, "owasp_findings": 0, "auth_issues": 0}])
    assert r["passed"] == 1
    assert r["healthy"]
