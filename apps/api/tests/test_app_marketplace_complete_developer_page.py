from app.services.app_marketplace_complete_developer_page import build_complete_developer_page

def test_page():
    p = build_complete_developer_page(
        developer={"display_name": "Dev Co", "slug": "dev-co", "verified": True},
        apps=[{"id": "app1", "name": "App", "slug": "app-one", "status": "published", "category": "connector", "install_count": 50}],
        stats={"total_installs": 50},
        recent_versions=[{"version": "2.0", "app_name": "App"}])
    assert p["page_type"] == "developer_profile"
    assert len(p["tabs"]) == 3
    assert "Dev Co" in p["seo"]["title"]

def test_empty():
    p = build_complete_developer_page(developer={"display_name": "New"}, apps=[], stats={}, recent_versions=[])
    assert p["app_count"] == 0
