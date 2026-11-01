from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_auto_cov import fleet_automation_coverage
def test_auto():
    r = fleet_automation_coverage([{"automated": True}] * 8 + [{"automated": False}] * 2)
    assert r["automated"] == 8
    assert r["coverage_pct"] == 80.0
    assert r["mature"]
