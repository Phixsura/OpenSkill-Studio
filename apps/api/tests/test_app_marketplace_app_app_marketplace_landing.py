from app.services.app_marketplace_app_app_marketplace_landing import build_landing_page

def test_landing():
    r = build_landing_page(
        featured_apps=[{"id": "a1", "name": "SuperApp", "icon": "🚀", "tagline": "Do more"}],
        categories=[{"id": "tools", "name": "Tools", "icon": "🔧", "app_count": 150}],
        stats={"total_apps": 500, "total_developers": 200, "total_downloads": 1000000},
        recent_apps=[{"id": "a2", "name": "NewApp", "icon": "✨"}],
    )
    assert r["hero"]["title"] == "Discover apps for your workflow"
    assert len(r["featured"]) == 1
    assert r["stats"]["total_apps"] == 500
    assert len(r["recent"]) == 1
