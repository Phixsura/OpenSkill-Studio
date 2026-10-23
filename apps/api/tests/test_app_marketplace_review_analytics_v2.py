from app.services.app_marketplace_review_analytics_v2 import analyze_reviews_v2

def test_analyze():
    reviews = [
        {"rating": 5, "created_at": "2026-10-01", "body": "Great tool works perfectly", "has_reply": True},
        {"rating": 4, "created_at": "2026-10-15", "body": "Good integration easy setup", "has_reply": False},
        {"rating": 2, "created_at": "2026-09-01", "body": "Slow performance needs improvement", "has_reply": True},
    ]
    r = analyze_reviews_v2(reviews=reviews)
    assert r["total"] == 3
    assert r["avg_rating"] > 3.5
    assert r["sentiment"]["positive"] == 2
    assert r["sentiment"]["negative"] == 1
    assert r["sentiment"]["nps"] > 0
    assert len(r["trends"]) == 2
    assert len(r["keywords"]) > 0
    assert r["reply_rate"] > 60

def test_empty():
    r = analyze_reviews_v2(reviews=[])
    assert r["total"] == 0
    assert r["avg_rating"] == 0
