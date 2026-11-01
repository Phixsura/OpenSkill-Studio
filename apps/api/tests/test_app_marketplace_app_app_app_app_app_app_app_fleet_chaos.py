from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_chaos import fleet_chaos_results
def test_chaos():
    r = fleet_chaos_results([{"passed": True}, {"passed": False, "weakness_found": True}])
    assert r["passed"] == 1
    assert r["weaknesses_found"] == 1
    assert not r["resilient"]
