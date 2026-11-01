from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dr import fleet_dr_readiness
def test_dr():
    r = fleet_dr_readiness([{"passed": True, "last_drill_days": 30}, {"passed": True, "last_drill_days": 60}])
    assert r["passed"] == 2
    assert r["last_drill_days"] == 60
    assert r["ready"]
