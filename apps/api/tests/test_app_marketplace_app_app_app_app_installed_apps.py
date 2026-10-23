from app.services.app_marketplace_app_app_app_app_installed_apps import build_installed_apps_page

def test_installed():
    apps = [
        {"id": "a1", "name": "SuperApp", "icon": "🚀", "version": "2.0.0", "api_calls_30d": 5000,
         "has_update": True, "update_version": "2.1.0"},
        {"id": "a2", "name": "Tool", "icon": "🔧", "version": "1.0.0", "api_calls_30d": 1000},
    ]
    r = build_installed_apps_page(apps=apps)
    assert r["total"] == 2
    assert r["total_api_calls"] == 6000
    assert r["updates_available"] == 1
    assert r["has_updates"]
