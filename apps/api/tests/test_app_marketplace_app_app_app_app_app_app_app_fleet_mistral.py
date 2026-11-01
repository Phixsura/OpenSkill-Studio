from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mistral import fleet_mistral_status
def test_mi():
    r = fleet_mistral_status([{"active": True, "completions_24h": 2000000, "tokens_24h": 1000000000}])
    assert r["completions_24h"] == 2000000
    assert r["all_active"]
