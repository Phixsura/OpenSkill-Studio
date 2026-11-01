from app.services.app_marketplace_app_app_app_app_app_app_app_app_settings_page import build_app_settings

def test_settings():
    r = build_app_settings({"name": "My App", "id": "app123"})
    assert r["app_name"] == "My App"
    assert len(r["sections"]) == 5
    assert r["sections"][0]["id"] == "general"
    assert r["sections"][-1]["id"] == "danger"
