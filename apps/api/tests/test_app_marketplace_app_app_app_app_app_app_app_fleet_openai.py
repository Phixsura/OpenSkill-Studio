from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_openai import fleet_openai_status
def test_oai():
    r = fleet_openai_status([{"active": True, "requests_24h": 2000000, "cost_usd_24h": 5000}])
    assert r["requests_24h"] == 2000000
    assert r["all_active"]
