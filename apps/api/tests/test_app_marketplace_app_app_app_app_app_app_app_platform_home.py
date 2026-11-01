from app.services.app_marketplace_app_app_app_app_app_app_app_platform_home import build_platform_home

def test_home():
    r = build_platform_home(
        user={"name": "Alice", "plan": "pro", "app_count": 5},
        featured_apps=[{"id": "a1", "name": "SuperApp", "icon": "🚀", "tagline": "Do more", "rating": 4.8}],
        trending_apps=[{"id": "a2", "name": "HotApp", "icon": "🔥", "growth_pct": 300}],
        categories=[{"id": "tools", "name": "Tools", "icon": "🔧", "count": 320}],
        platform_stats={"apps": 5200, "developers": 2000, "downloads": 12500000, "uptime_pct": 99.99})
    assert r["hero"]["title"] == "OpenSkill Marketplace"
    assert r["user"]["name"] == "Alice"
    assert r["stats"]["apps"] == 5200
    assert len(r["featured"]) == 1
    assert len(r["trending"]) == 1
    assert len(r["sections"]) == 5

def test_anonymous():
    r = build_platform_home(featured_apps=[], trending_apps=[], categories=[],
                             platform_stats={"apps": 100})
    assert r["user"] is None
