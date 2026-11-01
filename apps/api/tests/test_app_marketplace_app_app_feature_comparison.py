from app.services.app_marketplace_app_app_feature_comparison import compare_apps

def test_compare():
    apps = [
        {"id": "a", "name": "AppA", "features": {"SSO": True, "API": True, "Webhooks": False}},
        {"id": "b", "name": "AppB", "features": {"SSO": False, "API": True, "Support": "24/7"}},
    ]
    r = compare_apps(apps=apps, features=["SSO", "API", "Webhooks", "Support"])
    assert r["app_count"] == 2
    assert r["feature_count"] == 4
    assert r["rows"][0]["values"]["a"]["display"] == "✓"  # SSO
    assert r["rows"][0]["values"]["b"]["display"] == "✗"
    assert r["rows"][3]["values"]["b"]["display"] == "24/7"
    assert r["rows"][2]["values"]["b"]["display"] == "—"  # missing
