from app.services.app_marketplace_app_marketplace_complete_page import build_complete_marketplace_page

def test_anonymous():
    p = build_complete_marketplace_page(
        hero={"title": "Welcome"}, featured=[{"id": "f1"}] * 6, trending=[{"id": "t1"}] * 8,
        categories=[{"id": "c1"}] * 4, collections=[{"id": "col1"}] * 3,
        stats={"apps": 500}, testimonials=[{"quote": "Great!"}],
        footer={"copyright": "2026"}, seo={"title": "Marketplace"})
    assert p["page_type"] == "complete_marketplace"
    assert not p["personalized"]
    assert p["section_count"] == 8
    assert p["total_content_items"] == 21

def test_personalized():
    p = build_complete_marketplace_page(
        hero={}, featured=[], trending=[], categories=[], collections=[],
        stats={}, testimonials=[], footer={}, seo={}, user={"id": "u1"})
    assert p["personalized"]
    assert p["section_count"] == 9  # +1 for personalized section
