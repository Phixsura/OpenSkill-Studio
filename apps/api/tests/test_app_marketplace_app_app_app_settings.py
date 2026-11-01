from app.services.app_marketplace_app_app_app_settings import build_settings_page

def test_settings():
    app = {"name": "SuperApp", "description": "A great app", "published": True, "category": "tools"}
    r = build_settings_page(app=app)
    assert r["section_count"] == 3
    assert r["app_name"] == "SuperApp"
    general = r["sections"][0]
    assert general["id"] == "general"
    assert general["field_count"] == 4
    assert general["fields"][0]["value"] == "SuperApp"
