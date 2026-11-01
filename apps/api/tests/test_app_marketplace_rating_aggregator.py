from app.services.app_marketplace_rating_aggregator import compute_weighted_rating, build_distribution, sort_reviews_by_helpfulness

def test_weighted_rating():
    ratings = [{"score": 5}] * 20 + [{"score": 4}] * 10
    r = compute_weighted_rating(ratings=ratings)
    assert r["average"] > 4.5
    assert r["count"] == 30
    assert r["confidence"] == "medium"

def test_empty_ratings():
    r = compute_weighted_rating(ratings=[])
    assert r["average"] == 0

def test_high_confidence():
    r = compute_weighted_rating(ratings=[{"score": 4}] * 100)
    assert r["confidence"] == "high"

def test_distribution():
    d = build_distribution(ratings=[{"score": 5}, {"score": 5}, {"score": 3}, {"score": 1}])
    assert d["counts"]["5"] == 2
    assert d["counts"]["3"] == 1

def test_helpfulness_sort():
    reviews = [
        {"id": "a", "helpful_yes": 1, "helpful_no": 10},
        {"id": "b", "helpful_yes": 50, "helpful_no": 2},
        {"id": "c", "helpful_yes": 0, "helpful_no": 0},
    ]
    sorted_r = sort_reviews_by_helpfulness(reviews=reviews)
    assert sorted_r[0]["id"] == "b"
