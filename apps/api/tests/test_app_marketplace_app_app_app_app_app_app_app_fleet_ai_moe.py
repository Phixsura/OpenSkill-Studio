from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_moe import fleet_ai_moe
def test_moe():
    r = fleet_ai_moe([{"active": True, "experts": 64, "tokens_24h": 50000000000, "load_balance": 0.95}])
    assert r["experts"] == 64
    assert r["balanced"]
