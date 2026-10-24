from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_chef import fleet_chef_compliance
def test_chef():
    r = fleet_chef_compliance([{"passed": 90, "failed": 5, "skipped": 5}])
    assert r["compliance_pct"] == 90.0
    assert not r["compliant"]
