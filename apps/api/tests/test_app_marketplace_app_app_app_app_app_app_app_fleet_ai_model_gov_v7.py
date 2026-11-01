from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_gov_v7 import fleet_ai_model_governance_v7
def test_mgv7():
    r = fleet_ai_model_governance_v7([{"active": True, "models": 1000, "approved": 990, "rejected": 10, "compliance_pct": 99.5}])
    assert r["governed"]
