from app.services.app_marketplace_app_detail_v2 import build_app_detail_v2, get_app_detail_breadcrumb

def test_detail():
    d = build_app_detail_v2(
        app={"id": "a1", "name": "SuperApp", "slug": "super-app", "description": "Great", "category": "connector"},
        developer={"display_name": "DevCo", "verified": True},
        version={"version": "2.0"}, reviews={"count": 50, "avg": 4.5},
        install_stats={"total": 2000, "active": 1800},
        screenshots=[{"url": "s1.png"}], related=[{"id": "r1"}],
        changelog=[{"version": "2.0"}, {"version": "1.0"}], pricing={"plan": "free"})
    assert d["page_type"] == "app_detail_v2"
    assert "SuperApp" in d["seo"]["title"]
    assert len([t for t in d["tabs"] if t]) >= 4

def test_breadcrumb():
    b = get_app_detail_breadcrumb(app={"id": "a1", "name": "App", "slug": "app", "category": "connector"})
    assert len(b) == 3
    assert b[0]["label"] == "Marketplace"
    assert b[2]["label"] == "App"
