from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_anthropic import fleet_anthropic_status
def test_anth():
    r = fleet_anthropic_status([{"active": True, "requests_24h": 1000000, "tokens_24h": 500000000}])
    assert r["requests_24h"] == 1000000
    assert r["all_active"]
