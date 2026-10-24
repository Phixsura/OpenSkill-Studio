from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_readiness_assess import fleet_readiness_assessment
def test_assess():
    r = fleet_readiness_assessment([{"passed": True}, {"passed": True}, {"passed": False, "blocking": True}])
    assert r["passed"] == 2
    assert r["blockers"] == 1
    assert not r["launch_ready"]
