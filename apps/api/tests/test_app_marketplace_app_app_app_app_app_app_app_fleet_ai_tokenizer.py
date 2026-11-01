from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tokenizer import fleet_ai_tokenizer
def test_tok():
    r = fleet_ai_tokenizer([{"active": True, "vocab_size": 128000, "tokens_24h": 50000000000, "compression_ratio": 3.8}])
    assert r["vocab_size"] == 128000
    assert r["efficient"]
