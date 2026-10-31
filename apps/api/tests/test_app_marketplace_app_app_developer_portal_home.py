from app.services.app_marketplace_app_app_developer_portal_home import build_portal_home

def test_portal():
    r = build_portal_home(user_name="Alice", apps_count=5, total_installs=12000, notifications=3,
                           recent_deploys=[{"app": "MyApp", "version": "2.0.0", "status": "success"}],
                           announcements=[{"title": "SDK v3 Released!", "type": "feature"}])
    assert "Alice" in r["greeting"]
    assert r["stats"]["apps"] == 5
    assert len(r["quick_links"]) == 6
    assert len(r["recent_deploys"]) == 1
    assert len(r["announcements"]) == 1
