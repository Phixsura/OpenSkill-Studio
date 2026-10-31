from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cost_dash_v3 import fleet_ai_cost_dashboard_v3
def test_cdv3():
    r = fleet_ai_cost_dashboard_v3([{"active": True, "total_usd": 1000000, "savings_usd": 200000, "forecasts": 100}])
    assert r["savings_usd"] == 200000
    assert r["optimizing"]
