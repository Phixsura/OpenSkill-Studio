from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_gov_v2 import fleet_ai_model_governance_v2
def test_mgv2():
    r = fleet_ai_model_governance_v2([{"active": True, "models": 500, "policies": 200, "compliance_pct": 99, "approvals_24h": 50}])
    assert r["compliance"] == 99.0
    assert r["governed"]
