from app.services.app_marketplace_app_app_app_app_app_app_app_app_compare import compare_apps

def test_compare():
    r = compare_apps([
        {"name": "App A", "rating": 4.5, "features": {"sso": True, "webhooks": True, "analytics": False}},
        {"name": "App B", "rating": 4.0, "features": {"sso": False, "webhooks": True, "analytics": True}},
    ])
    assert r["app_count"] == 2
    assert r["feature_count"] == 3
    assert r["columns"][0]["feature_values"]["sso"] is True
    assert r["columns"][1]["feature_values"]["sso"] is False

def test_too_few():
    r = compare_apps([{"name": "Only One"}])
    assert "error" in r
