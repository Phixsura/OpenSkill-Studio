from app.services.app_marketplace_app_review_moderation import moderate_review, bulk_moderate

def test_approve():
    r = moderate_review(text="Great app, works perfectly for my workflow!", rating=5, reviewer_id="u1")
    assert r["action"] == "approve"
    assert r["flag_count"] == 0

def test_blocked():
    r = moderate_review(text="This is a scam do not install", rating=1, reviewer_id="u2")
    assert r["action"] == "reject"

def test_low_effort():
    r = moderate_review(text="Bad.", rating=1, reviewer_id="u3")
    assert r["action"] == "review"
    assert any(f["type"] == "low_effort" for f in r["flags"])

def test_bulk():
    reviews = [{"id": "u1", "text": "Awesome tool really love it!", "rating": 5},
               {"id": "u2", "text": "scam alert", "rating": 1}]
    r = bulk_moderate(reviews=reviews)
    assert r["total"] == 2
    assert r["approved"] == 1
    assert r["rejected"] == 1
