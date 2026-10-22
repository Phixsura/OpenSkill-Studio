from app.services.app_marketplace_app_review_page_builder import build_review_page

def test_page():
    p = build_review_page(reviews=[{"rating": 5}], average=4.5, count=10, distribution={5: 6, 4: 3, 3: 1})
    assert p["has_reviews"] is True
    assert p["average"] == 4.5
