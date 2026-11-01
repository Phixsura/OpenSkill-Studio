from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kubecost import fleet_kubecost_status
def test_kc():
    r = fleet_kubecost_status([{"monthly_cost_usd": 10000, "savings_available_usd": 2000}])
    assert r["monthly_cost"] == 10000
    assert r["savings_pct"] == 20.0
