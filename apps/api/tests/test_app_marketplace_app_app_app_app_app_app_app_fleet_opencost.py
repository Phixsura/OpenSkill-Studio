from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_opencost import fleet_opencost_status
def test_oc():
    r = fleet_opencost_status([{"daily_cost_usd": 100, "idle_cost_usd": 20}, {"daily_cost_usd": 50, "idle_cost_usd": 10}])
    assert r["daily_cost"] == 150
    assert r["efficiency_pct"] == 80.0
