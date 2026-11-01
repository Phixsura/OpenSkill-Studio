from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_attention import fleet_ai_attention
def test_att():
    r = fleet_ai_attention([{"active": True, "heads": 128, "sequences_24h": 10000000, "sparsity_pct": 75}])
    assert r["heads"] == 128
    assert r["efficient"]
