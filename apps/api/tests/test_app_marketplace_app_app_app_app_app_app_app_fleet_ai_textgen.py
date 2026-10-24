from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_textgen import fleet_ai_textgen
def test_tg():
    r = fleet_ai_textgen([{"active": True, "generations_24h": 2000000, "tokens_24h": 500000000}])
    assert r["generations_24h"] == 2000000
    assert r["all_active"]
