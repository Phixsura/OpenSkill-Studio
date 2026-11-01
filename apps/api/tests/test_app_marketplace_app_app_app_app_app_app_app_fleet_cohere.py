from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cohere import fleet_cohere_status
def test_co():
    r = fleet_cohere_status([{"active": True, "embed_calls_24h": 5000000, "generate_calls_24h": 1000000}])
    assert r["embed_calls"] == 5000000
    assert r["all_active"]
