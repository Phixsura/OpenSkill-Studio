from app.services.app_marketplace_app_app_app_app_app_app_app_storage_usage import analyze_storage, storage_forecast

def test_analyze():
    r = analyze_storage([
        {"type": "database", "size_gb": 100, "tenant": "acme"},
        {"type": "blob", "size_gb": 500, "tenant": "acme"},
        {"type": "database", "size_gb": 50, "tenant": "beta"},
    ])
    assert r["total_gb"] == 650
    assert r["by_type"]["blob"] == 500

def test_forecast():
    r = storage_forecast(800, 50, 1000)
    assert r["months_until_full"] == 4
    assert not r["action_needed"]  # 80% is not > 80
