from app.services.app_marketplace_app_app_review_summary import build_review_summary

def test_positive():
    reviews = [{"rating": 5}, {"rating": 5}, {"rating": 4}, {"rating": 4}, {"rating": 3}]
    r = build_review_summary(reviews=reviews)
    assert r["avg_rating"] == 4.2
    assert r["sentiment"] == "positive"
    assert r["positive_pct"] == 80.0

def test_negative():
    reviews = [{"rating": 1}, {"rating": 2}, {"rating": 1}, {"rating": 2}, {"rating": 3}]
    r = build_review_summary(reviews=reviews)
    assert r["sentiment"] == "negative"

def test_empty():
    r = build_review_summary(reviews=[])
    assert r["total"] == 0
    assert r["sentiment"] == "neutral"
