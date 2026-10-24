from app.services.app_marketplace_complete_collection_page import build_complete_collection_page

def test_page():
    p = build_complete_collection_page(
        collection={"title": "Best Tools", "slug": "best-tools", "description": "Top picks", "type": "editorial"},
        apps=[{"id": "a1"}, {"id": "a2"}],
        curator={"display_name": "Team", "slug": "team", "verified": True},
        related_collections=[{"title": "New Apps"}])
    assert p["page_type"] == "collection_detail"
    assert p["app_count"] == 2
    assert p["curator"]["verified"]
    assert "Best Tools" in p["seo"]["title"]
