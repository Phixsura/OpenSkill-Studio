from app.services.app_marketplace_complete_installed_apps_page import build_installed_apps_page

def test_page():
    installs = [
        {"name": "App1", "status": "active", "category": "connector", "update_available": True},
        {"name": "App2", "status": "active", "category": "analytics"},
        {"name": "App3", "status": "uninstalled", "category": "connector"},
    ]
    p = build_installed_apps_page(installations=installs, categories=["connector", "analytics"])
    assert p["stats"]["total"] == 2  # only active
    assert p["stats"]["update_available"] == 1
    assert p["stats"]["categories_used"] == 2
    assert len(p["bulk_actions"]) == 2
