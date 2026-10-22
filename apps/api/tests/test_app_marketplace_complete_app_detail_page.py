from app.services.app_marketplace_complete_app_detail_page import build_complete_app_detail_page

def test_full():
    p = build_complete_app_detail_page(
        app={"id": "a1", "name": "SuperApp", "slug": "super-app", "description": "D", "category": "connector", "status": "published"},
        developer={"display_name": "DevCo", "slug": "devco", "verified": True},
        versions=[{"version": "2.0"}, {"version": "1.0"}],
        reviews={"average": 4.5, "count": 100},
        install_stats={"total": 500, "active": 450},
        screenshots=[{"url": "s1.png"}], related_apps=[{"id": "r1"}],
        documentation=[{"slug": "intro"}, {"slug": "api"}])
    assert p["page_type"] == "app_detail"
    assert p["current_version"]["version"] == "2.0"
    assert p["version_count"] == 2
    assert len(p["tabs"]) == 5
    assert p["developer"]["verified"]

def test_empty():
    p = build_complete_app_detail_page(
        app={"id": "a1", "name": "X"}, developer={"display_name": "D"},
        versions=[], reviews={}, install_stats={}, screenshots=[], related_apps=[], documentation=[])
    assert p["current_version"] is None
    assert p["documentation_pages"] == 0
