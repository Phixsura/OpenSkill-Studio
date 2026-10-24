from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ollama import fleet_ollama_status
def test_ollama():
    r = fleet_ollama_status([{"running": True, "models_loaded": 3, "requests_24h": 100000}])
    assert r["models_loaded"] == 3
    assert r["all_running"]
