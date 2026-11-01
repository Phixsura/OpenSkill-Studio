from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_spec_dec import fleet_ai_spec_decoding
def test_sd():
    r = fleet_ai_spec_decoding([{"active": True, "tokens_24h": 10000000000, "acceptance_pct": 78, "speedup_x": 2.8}])
    assert r["acceptance_rate"] == 78.0
    assert r["fast"]
