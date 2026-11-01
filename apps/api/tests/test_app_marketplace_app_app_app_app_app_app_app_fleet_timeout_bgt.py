from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_timeout_bgt import fleet_timeout_budget
def test_tb():
    r = fleet_timeout_budget([{"actual_ms": 2000, "budget_ms": 5000}, {"actual_ms": 6000, "budget_ms": 5000}])
    assert r["over_budget"] == 1
    assert not r["healthy"]
