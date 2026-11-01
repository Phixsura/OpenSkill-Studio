from app.services.app_marketplace_app_app_app_reviews_page import build_reviews_page

def test_page():
    reviews = [
        {"id": "r1", "rating": 5, "title": "Great!", "body": "Love it", "author": "Alice",
         "created_at": "2026-01-02", "helpful_count": 10},
        {"id": "r2", "rating": 3, "title": "OK", "body": "Average", "author": "Bob",
         "created_at": "2026-01-01", "helpful_count": 2},
    ]
    r = build_reviews_page(app_name="SuperApp", reviews=reviews)
    assert r["total"] == 2
    assert r["avg_rating"] == 4.0
    assert r["reviews"][0]["title"] == "Great!"  # newest first

def test_filter():
    reviews = [{"id": "1", "rating": 5}, {"id": "2", "rating": 3}]
    r = build_reviews_page(app_name="X", reviews=reviews, filter_rating=5)
    assert r["shown"] == 1
