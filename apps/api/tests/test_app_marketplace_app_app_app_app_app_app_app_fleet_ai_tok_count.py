from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tok_count import fleet_ai_token_counter
def test_tc():
    r = fleet_ai_token_counter([{"active": True, "input_tokens": 50000000000, "output_tokens": 10000000000, "cost_usd": 15000}])
    assert r["cost_usd"] == 15000
    assert r["metered"]
