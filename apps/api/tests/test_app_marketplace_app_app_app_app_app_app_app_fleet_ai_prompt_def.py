from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_prompt_def import fleet_ai_prompt_defense
def test_pd():
    r = fleet_ai_prompt_defense([{"active": True, "scanned_24h": 10000000, "blocked_24h": 500, "fp_rate": 0.1}])
    assert r["blocked_24h"] == 500
    assert r["secure"]
