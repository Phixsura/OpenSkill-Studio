from app.services.app_marketplace_app_app_app_app_app_app_app_marketplace_home import build_marketplace_home

def test_home():
    r = build_marketplace_home(
        featured_apps=[{"name": "Slack Bot", "icon": "💬", "rating": 4.8, "installs": 50000}],
        categories=[{"id": "tools", "label": "Tools", "icon": "🛠️", "count": 120}],
        trending=[{"name": "Hot App", "icon": "🔥"}],
        new_apps=[{"name": "Fresh", "icon": "🆕"}],
        total_apps=500, total_developers=200)
    assert r["hero"]["title"] == "OpenSkill Marketplace"
    assert "500" in r["hero"]["subtitle"]
    assert len(r["featured"]) == 1
    assert len(r["categories"]) == 1
    assert r["stats"]["apps_display"] == "500"
