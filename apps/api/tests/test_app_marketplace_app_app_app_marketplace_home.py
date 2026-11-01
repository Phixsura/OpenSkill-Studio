from app.services.app_marketplace_app_app_app_marketplace_home import build_marketplace_home

def test_home():
    r = build_marketplace_home(
        featured=[{"id": "a1", "name": "SuperApp", "icon": "🚀", "tagline": "Do more", "rating": 4.8}],
        trending=[{"id": "a2", "name": "HotApp", "icon": "🔥", "growth_pct": 250}],
        categories=[{"id": "tools", "name": "Tools", "icon": "🔧", "count": 150}],
        new_apps=[{"id": "a3", "name": "FreshApp", "icon": "🆕"}],
        total_apps=5200, total_developers=1800,
    )
    assert r["hero"]["title"] == "OpenSkill Marketplace"
    assert r["hero"]["stats"]["total_apps"] == 5200
    assert len(r["featured"]) == 1
    assert len(r["trending"]) == 1
    assert r["section_count"] == 4
