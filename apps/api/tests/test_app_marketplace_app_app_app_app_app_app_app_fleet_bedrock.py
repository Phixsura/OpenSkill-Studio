from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bedrock import fleet_bedrock_status
def test_br():
    r = fleet_bedrock_status([{"available": True, "invocations_24h": 1000000, "tokens_24h": 500000000}])
    assert r["invocations_24h"] == 1000000
    assert r["all_available"]
