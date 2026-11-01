from app.services.app_developer_profile_page_builder import build_developer_profile_page

def test_page():
    p = build_developer_profile_page(
        developer={"display_name": "Dev Co", "verified": True},
        apps=[{"name": "A", "status": "published", "category": "connector", "install_count": 50}],
        stats={"total_installs": 50, "avg_health": 95})
    assert p["app_count"] == 1
    assert p["verified"] is True
    assert len(p["breadcrumbs"]) == 3

def test_no_apps():
    p = build_developer_profile_page(developer={"display_name": "New"}, apps=[], stats={})
    assert p["app_count"] == 0
