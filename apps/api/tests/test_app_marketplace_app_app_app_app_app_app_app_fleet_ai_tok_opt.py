from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tok_opt import fleet_ai_token_optimizer
def test_to():
    r = fleet_ai_token_optimizer([{"active": True, "optimized_24h": 10000000, "tokens_saved": 5000000000, "savings_pct": 35}])
    assert r["savings_pct"] == 35.0
    assert r["efficient"]
