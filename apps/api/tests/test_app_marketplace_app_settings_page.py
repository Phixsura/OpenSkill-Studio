from app.services.app_marketplace_app_settings_page import build_app_settings_page

def test_settings():
    p = build_app_settings_page(
        app={"id": "a1", "name": "App", "slug": "app", "status": "published", "category": "connector"},
        config={"timeout": 30}, api_keys=[{"name": "prod", "prefix": "osk_"}],
        webhooks=[{"url": "https://x.com"}], team=[{"id": "u1"}],
        env_vars=[{"key": "API_URL"}], domains=[{"domain": "app.example.com"}])
    assert p["tab_count"] == 7
    assert p["tabs"][1]["title"] == "API Keys (1)"
    assert p["tabs"][3]["title"] == "Team (1)"

def test_empty():
    p = build_app_settings_page(app={"id": "a1", "name": "X"}, config={},
                                   api_keys=[], webhooks=[], team=[], env_vars=[], domains=[])
    assert p["tabs"][1]["title"] == "API Keys (0)"
