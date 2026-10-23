from app.services.app_marketplace_app_app_app_app_app_app_app_rating_agg import aggregate_ratings, wilson_score

def test_aggregate():
    reviews = [{"rating": 5}, {"rating": 4}, {"rating": 5}, {"rating": 3}, {"rating": 4},
               {"rating": 5}, {"rating": 4}, {"rating": 5}, {"rating": 2}, {"rating": 4}]
    r = aggregate_ratings(reviews)
    assert r["count"] == 10
    assert r["average"] == 4.1
    assert r["distribution"][5] == 4
    assert r["sentiment"] == "positive"
    assert r["wilson_score"] > 0

def test_wilson():
    assert wilson_score(95, 100) > wilson_score(9, 10)  # more data = higher confidence
    assert wilson_score(0, 0) == 0.0
