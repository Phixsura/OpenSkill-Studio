from app.services.app_marketplace_review_moderation import moderate_review, filter_reviews

def test_approved():
    r = moderate_review(text="Great app, works well!", rating=5, reviewer_id="u1", app_developer_id="dev1")
    assert r["status"] == "approved"

def test_self_review_rejected():
    r = moderate_review(text="My own app is great!", rating=5, reviewer_id="dev1", app_developer_id="dev1")
    assert r["status"] == "rejected"
    assert any(f["type"] == "self_review" for f in r["flags"])

def test_flagged_content():
    r = moderate_review(text="This is a total scam, avoid it", rating=1, reviewer_id="u1", app_developer_id="dev1")
    assert r["status"] == "pending_review"

def test_too_short():
    r = moderate_review(text="Bad", rating=1, reviewer_id="u1", app_developer_id="dev1")
    assert any(f["type"] == "too_short" for f in r["flags"])

def test_filter_by_rating():
    reviews = [{"rating": 5, "text": "A"}, {"rating": 2, "text": "B"}, {"rating": 4, "text": "C"}]
    assert len(filter_reviews(reviews=reviews, min_rating=4)) == 2

def test_filter_verified():
    reviews = [{"verified_purchase": True}, {"verified_purchase": False}]
    assert len(filter_reviews(reviews=reviews, verified_only=True)) == 1
