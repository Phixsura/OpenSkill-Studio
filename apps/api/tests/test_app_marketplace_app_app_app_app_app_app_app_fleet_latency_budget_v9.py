from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_latency_budget_v9 import fleet_latency_budget_v9
def test_lb2_v9():
    r = fleet_latency_budget_v9([{"p99_ms": 50, "budget_ms": 200}])
    assert r["within_budget"] == 1
    assert r["healthy"]
