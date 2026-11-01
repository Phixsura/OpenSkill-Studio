from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_governance import fleet_ai_governance
def test_gov():
    r = fleet_ai_governance([{"active": True, "policies": 200, "violations_24h": 3, "compliance_pct": 99.5}])
    assert r["compliance_pct"] == 99.5
    assert r["governed"]
