from app.services.app_marketplace_review_system_v2 import create_review_v2, compute_review_stats_v2, sort_reviews

def test_create():
    r = create_review_v2(app_id="a1", user_id="u1", rating=5, title="Great app!",
                          pros=["Fast", "Easy"], cons=["No dark mode"], body="Love it", verified_purchase=True)
    assert r["status"] == "published"
    assert r["verified_purchase"]

def test_invalid_rating():
    r = create_review_v2(app_id="a1", user_id="u1", rating=6, title="Test review",
                          pros=[], cons=[], body="")
    assert r["error"]

def test_stats():
    reviews = [{"rating": 5, "verified_purchase": True}, {"rating": 4, "verified_purchase": False},
               {"rating": 5, "verified_purchase": True}]
    s = compute_review_stats_v2(reviews=reviews)
    assert s["avg_rating"] > 4.5
    assert s["distribution"]["5"] == 2
    assert s["verified_pct"] > 60

def test_sort_helpful():
    reviews = [{"helpful_yes": 10}, {"helpful_yes": 50}, {"helpful_yes": 5}]
    r = sort_reviews(reviews=reviews, sort_by="helpful")
    assert r[0]["helpful_yes"] == 50
