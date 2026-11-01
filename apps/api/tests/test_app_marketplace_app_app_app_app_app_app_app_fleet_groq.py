from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_groq import fleet_groq_status
def test_groq():
    r = fleet_groq_status([{"active": True, "tokens_per_sec": 1000, "requests_24h": 5000000}])
    assert r["tokens_per_sec"] == 1000
    assert r["blazing"]
