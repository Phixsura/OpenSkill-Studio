from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tokenizer import fleet_tokenizer_status
def test_tok():
    r = fleet_tokenizer_status([{"active": True, "tokens_24h": 1000000000, "vocabularies": 5}])
    assert r["tokens_24h"] == 1000000000
    assert r["all_active"]
