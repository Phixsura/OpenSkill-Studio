from app.services.app_marketplace_complete_category_page import build_complete_category_page

def test_page():
    p = build_complete_category_page(category="connector", apps=[{"name": "A"}], total=50, page=1, per_page=20, trending=[{"name": "B"}])
    assert p["page_type"] == "category"
    assert "Connector" in p["seo"]["title"]
    assert len(p["trending_in_category"]) == 1
