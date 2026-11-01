from app.services.app_marketplace_app_app_review_insight import analyze_review_insights

def test_insights():
    reviews = [
        {"text": "Great app, love the design! Amazing features.", "rating": 5, "tags": ["ui", "features"]},
        {"text": "Terrible performance, crashes often. Bad experience.", "rating": 1, "tags": ["performance", "stability"]},
        {"text": "Good app overall, easy to use.", "rating": 4, "tags": ["usability"]},
    ]
    r = analyze_review_insights(reviews=reviews)
    assert r["total_reviews"] == 3
    assert r["sentiment"]["positive"] == 2
    assert r["sentiment"]["negative"] == 1
    assert r["sentiment_score"] > 0
    assert r["avg_rating"] > 3

def test_empty():
    r = analyze_review_insights(reviews=[])
    assert "error" in r
