from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_prompts import fleet_ai_prompts
def test_prompts():
    r = fleet_ai_prompts([{"prompts": 200, "versions": 1000, "evaluations_24h": 50000}])
    assert r["prompts"] == 200
    assert r["managed"]
