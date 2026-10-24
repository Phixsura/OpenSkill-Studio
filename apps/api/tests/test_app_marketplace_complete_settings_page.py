from app.services.app_marketplace_complete_settings_page import build_complete_settings_page

def test_settings():
    p = build_complete_settings_page(
        app={"id": "a1", "name": "MyApp", "status": "published", "description": "D", "category": "connector"},
        api_keys=[{"name": "prod", "prefix": "osk_"}],
        webhooks=[{"url": "https://x.com/hook", "active": True}],
        team_members=[{"user_id": "u1", "role": "owner"}],
        config={"timeout": 30})
    assert p["page_type"] == "app_settings"
    assert len(p["sections"]) == 5
    assert p["sections"][1]["title"] == "API Keys (1)"

def test_empty():
    p = build_complete_settings_page(app={"id": "a1", "name": "X"}, api_keys=[], webhooks=[], team_members=[], config={})
    assert p["sections"][2]["title"] == "Webhooks (0)"
