from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ci_analytics_v9 import fleet_ci_analytics_v9
def test_cia_v9():
    r = fleet_ci_analytics_v9([{"runs_today": 500, "success_rate": 99, "avg_duration_sec": 120, "flaky_tests": 2}])
    assert r["avg_success_rate"] == 99.0
    assert r["healthy"]
