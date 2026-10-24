from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cost_gov_v7 import fleet_ai_cost_governance_v7
def test_cgv7():
    r = fleet_ai_cost_governance_v7([{"active": True, "budgets": 50, "spend_usd": 5000000, "within": True}])
    assert r["governed"]
    assert r["within_budget"]
