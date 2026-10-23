from app.services.app_marketplace_app_app_app_app_app_app_app_portal_home import build_portal_home

def test_portal():
    r = build_portal_home(user_name="Alice", app_count=5, api_calls_today=150000,
                            unread_notifications=3, recent_deploys=2,
                            achievement_count=8, level_title="Builder")
    assert "Alice" in r["greeting"]
    assert len(r["stats_bar"]) == 5
    assert len(r["quick_links"]) == 4
    assert r["stats_bar"][1]["value"] == "150,000"
