from app.services.app_marketplace_app_app_app_app_app_app_app_recommend_engine import recommend_apps, get_because_you_use

def test_recommend():
    all_apps = [
        {"id": "a1", "name": "Slack Bot", "category": "comm", "installs": 50000, "rating": 4.8, "verified": True},
        {"id": "a2", "name": "GitHub Sync", "category": "dev", "installs": 30000, "rating": 4.5},
        {"id": "a3", "name": "Analytics Pro", "category": "analytics", "installs": 10000, "rating": 4.2},
    ]
    r = recommend_apps(user_apps=["a3"], user_categories=["comm"], all_apps=all_apps, limit=2)
    assert len(r) == 2
    assert r[0]["id"] == "a1"  # category match + high installs

def test_because():
    r = get_because_you_use(
        installed_app={"id": "a1", "name": "Slack Bot", "category": "comm"},
        all_apps=[
            {"id": "a1", "name": "Slack Bot", "category": "comm", "rating": 4.8},
            {"id": "a2", "name": "Discord Bot", "category": "comm", "rating": 4.5},
            {"id": "a3", "name": "Unrelated", "category": "dev", "rating": 5.0},
        ])
    assert len(r) == 1
    assert r[0]["name"] == "Discord Bot"
    assert "Slack Bot" in r[0]["reason"]
