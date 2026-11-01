from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_compliance_report_v9 import fleet_compliance_report_v9
def test_cr3_v9():
    r = fleet_compliance_report_v9([{"generated": True, "framework": "SOC2", "findings": 0}])
    assert r["frameworks"] == 1
    assert r["healthy"]
