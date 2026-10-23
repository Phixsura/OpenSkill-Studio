from app.services.app_marketplace_complete_developer_profile_page import build_complete_developer_profile_page

def test_profile():
    p = build_complete_developer_profile_page(
        developer={"display_name": "DevCo", "slug": "devco", "bio": "We build tools", "verified": True, "created_at": "2024-01-01"},
        apps=[{"id": "a1", "name": "App1", "slug": "app1", "status": "published", "install_count": 500, "category": "connector"},
              {"id": "a2", "name": "App2", "status": "draft", "install_count": 0}],
        badges=[{"label": "Verified"}], achievements=[{"title": "First App"}],
        stats={}, reviews_summary={"avg_rating": 4.5, "total_reviews": 100})
    assert p["stats"]["published_apps"] == 1
    assert p["stats"]["total_installs"] == 500
    assert len(p["apps"]) == 1  # only published
    assert "DevCo" in p["seo"]["title"]
