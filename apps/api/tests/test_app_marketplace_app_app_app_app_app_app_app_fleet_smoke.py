from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_smoke import fleet_smoke_tests
def test_smoke():
    r = fleet_smoke_tests([{"smoke_passed": True}, {"smoke_passed": True}, {"smoke_passed": False}])
    assert r["passed"] == 2
    assert r["failed"] == 1
    assert not r["all_passed"]
