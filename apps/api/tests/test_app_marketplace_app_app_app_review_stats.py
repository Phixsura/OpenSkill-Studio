from app.services.app_marketplace_app_app_app_review_stats import build_review_stats

def test_stats():
    reviews = [{"rating": 5}, {"rating": 5}, {"rating": 4}, {"rating": 3}, {"rating": 1}]
    r = build_review_stats(reviews=reviews)
    assert r["total"] == 5
    assert r["avg_rating"] == 3.6
    assert r["distribution"][5] == 2
    assert r["sentiment"]["positive"] == 3
    assert r["sentiment"]["negative"] == 1
    assert r["nps"] == 20  # (2 promoters - 1 detractor) / 5 * 100

def test_empty():
    r = build_review_stats(reviews=[])
    assert r["total"] == 0
    assert r["avg_rating"] == 0
