from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_governance import fleet_ai_governance
def test_gov():
    r = fleet_ai_governance([{"active": True, "policies": 50, "reviews_24h": 1000}])
    assert r["policies"] == 50
    assert r["governed"]
