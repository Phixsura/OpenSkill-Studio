from app.services.app_marketplace_app_app_rating_breakdown import analyze_ratings

def test_analyze():
    ratings = [{"rating": 5}, {"rating": 5}, {"rating": 4}, {"rating": 3}, {"rating": 5}]
    r = analyze_ratings(ratings=ratings)
    assert r["total"] == 5
    assert r["avg"] == 4.4
    assert r["distribution"][5] == 3
    assert r["five_star_pct"] == 60.0

def test_improving():
    ratings = [{"rating": 3}] * 5 + [{"rating": 5}] * 5
    r = analyze_ratings(ratings=ratings)
    assert r["trend"] == "improving"

def test_empty():
    r = analyze_ratings(ratings=[])
    assert r["total"] == 0
    assert r["trend"] == "stable"
