from app.services.app_marketplace_app_developer_app_marketplace_review_analytics import compute_rating_trends, analyze_review_sentiment, find_common_keywords

def test_trends():
    reviews = [{"rating": 5, "created_at": "2026-01-15"}, {"rating": 4, "created_at": "2026-01-20"},
               {"rating": 3, "created_at": "2026-02-10"}]
    t = compute_rating_trends(reviews=reviews)
    assert len(t) == 2
    assert t[0]["month"] == "2026-01"
    assert t[0]["avg_rating"] == 4.5

def test_sentiment():
    reviews = [{"rating": 5}] * 7 + [{"rating": 3}] * 2 + [{"rating": 1}]
    s = analyze_review_sentiment(reviews=reviews)
    assert s["positive"] == 7
    assert s["negative"] == 1
    assert s["nps_estimate"] == 60.0

def test_keywords():
    reviews = [{"text": "Great integration tool"}, {"text": "Amazing integration"}, {"text": "Love this integration"}]
    k = find_common_keywords(reviews=reviews, min_count=2)
    assert any(kw["word"] == "integration" for kw in k)
