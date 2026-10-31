from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_adapt import fleet_ai_model_adapter
def test_ma():
    r = fleet_ai_model_adapter([{"active": True, "providers": ["openai", "anthropic", "google", "meta", "cohere", "mistral"], "translations_24h": 50000000}])
    assert r["providers"] == 6
    assert r["universal"]
