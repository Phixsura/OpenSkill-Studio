from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_token_cnt import fleet_ai_token_counter
def test_tc():
    r = fleet_ai_token_counter([{"input_tokens_24h": 1000000000, "output_tokens_24h": 500000000, "cost_24h": 10000}])
    assert r["input_tokens"] == 1000000000
    assert r["total_cost"] == 10000
