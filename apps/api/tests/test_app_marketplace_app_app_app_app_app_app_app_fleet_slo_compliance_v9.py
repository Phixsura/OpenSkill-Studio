from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_slo_compliance_v9 import fleet_slo_compliance_v9
def test_sloc_v9():
    r = fleet_slo_compliance_v9([{"met": True, "at_risk": False, "breached": False, "attainment_pct": 99.9}])
    assert r["met"] == 1
    assert r["healthy"]
