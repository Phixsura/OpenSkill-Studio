from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_compliance_scanner_v9 import fleet_compliance_scanner_v9
def test_comp_v9():
    r = fleet_compliance_scanner_v9([{"passed": True, "framework": "SOC2"}, {"passed": True, "framework": "ISO27001"}])
    assert r["passed"] == 2
    assert r["frameworks"] == 2
    assert r["healthy"]
