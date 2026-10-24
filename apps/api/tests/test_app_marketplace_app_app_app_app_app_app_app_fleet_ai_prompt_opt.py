from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_prompt_opt import fleet_ai_prompt_optimizer
def test_po():
    r = fleet_ai_prompt_optimizer([{"active": True, "optimized_24h": 10000, "improvement_pct": 25, "tokens_saved": 50000000}])
    assert r["improvement_pct"] == 25.0
    assert r["effective"]
