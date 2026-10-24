from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_compliance import fleet_ai_compliance
def test_aic():
    r = fleet_ai_compliance([{"passed": True, "regulation": "EU_AI_Act", "audits": 5}])
    assert r["regulations"] == 1
    assert r["compliant"]
