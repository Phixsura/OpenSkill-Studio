from app.services.app_marketplace_developer_page_v2 import build_developer_page_v2

def test_page():
    p = build_developer_page_v2(
        developer={"display_name": "DevCo", "slug": "devco", "bio": "We build tools", "verified": True},
        apps=[{"id": "a1", "name": "App1", "status": "published", "install_count": 500, "category": "connector"},
              {"id": "a2", "name": "App2", "status": "draft", "install_count": 0}],
        badges=[{"type": "verified"}], reviews_summary={"avg_rating": 4.5},
        achievements=[{"title": "First App"}])
    assert p["page_type"] == "developer_profile_v2"
    assert p["stats"]["published_apps"] == 1
    assert p["stats"]["total_installs"] == 500
    assert len(p["apps"]) == 1  # only published
    assert "DevCo" in p["seo"]["title"]
