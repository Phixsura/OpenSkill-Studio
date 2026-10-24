from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_vercel_ai import fleet_vercel_ai_status
def test_vai():
    r = fleet_vercel_ai_status([{"deployed": True, "streams_24h": 500000, "tokens_24h": 100000000}])
    assert r["streams_24h"] == 500000
    assert r["all_deployed"]
