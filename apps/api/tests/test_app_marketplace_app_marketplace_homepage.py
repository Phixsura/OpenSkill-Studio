from app.services.app_marketplace_app_marketplace_homepage import build_marketplace_homepage

def test_homepage():
    featured = [{"id": f"f{i}", "name": f"App {i}"} for i in range(8)]
    trending = [{"id": f"t{i}", "name": f"Trending {i}"} for i in range(4)]
    categories = [{"id": "tools", "name": "Tools", "count": 50}]
    stats = {"total_apps": 500, "total_developers": 200, "total_installs": 100000, "avg_rating": 4.5}
    announcements = [{"title": "New feature!", "body": "Dark mode"}]
    r = build_marketplace_homepage(featured_apps=featured, trending_apps=trending,
        categories=categories, stats=stats, announcements=announcements)
    assert r["hero"]["app_count"] == 500
    assert len(r["featured"]["apps"]) == 6  # capped
    assert len(r["trending"]["apps"]) == 4
    assert r["stats"]["total_installs"] == 100000
    assert r["sections_count"] == 5

def test_empty():
    r = build_marketplace_homepage(featured_apps=[], trending_apps=[], categories=[],
        stats={}, announcements=[])
    assert r["hero"]["app_count"] == 0
    assert len(r["featured"]["apps"]) == 0
