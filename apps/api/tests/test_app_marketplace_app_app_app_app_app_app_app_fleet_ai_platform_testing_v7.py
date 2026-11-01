from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_testing_v7 import fleet_ai_testing_v7
def test_tv7():
    r = fleet_ai_testing_v7([{"active": True, "tests": 500000, "coverage_pct": 95, "flaky_pct": 0.3}])
    assert r["coverage"] == 95.0
    assert r["reliable"]
