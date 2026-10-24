from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_token_budg import fleet_ai_token_budget
def test_tb():
    r = fleet_ai_token_budget([{"active": True, "allocated": 100000000, "used": 75000000, "cost_usd": 1500.50}])
    assert r["utilization"] == 75.0
    assert r["within_budget"]
    assert r["cost_usd"] == 1500.50
