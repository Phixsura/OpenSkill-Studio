from app.services.app_marketplace_category_page_builder import build_category_page

def test_page():
    p = build_category_page(category="connector", apps=[{"name": "A"}], total=50, page=1, per_page=20)
    assert p["category"] == "connector"
    assert p["total_pages"] == 3
    assert "Connect" in p["description"]

def test_unknown_cat():
    p = build_category_page(category="unknown", apps=[], total=0, page=1, per_page=20)
    assert p["description"] == ""
