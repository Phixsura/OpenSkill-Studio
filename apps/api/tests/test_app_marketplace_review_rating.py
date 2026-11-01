from app.services.app_marketplace_review_rating import add_review, get_reviews, get_rating_summary

APP = "review-app"

def test_add_review():
    r = add_review(app_id=APP, user_id="u1", rating=5, comment="Great!")
    assert r is not None
    assert r["rating"] == 5

def test_invalid_rating():
    assert add_review(app_id="x", user_id="u", rating=0) is None
    assert add_review(app_id="x", user_id="u", rating=6) is None

def test_duplicate_blocked():
    add_review(app_id="dup-app", user_id="u1", rating=4)
    assert add_review(app_id="dup-app", user_id="u1", rating=3) is None

def test_get_reviews():
    add_review(app_id="get-app", user_id="u1", rating=5)
    add_review(app_id="get-app", user_id="u2", rating=4)
    assert len(get_reviews("get-app")) == 2

def test_rating_summary():
    app = "sum-app"
    add_review(app_id=app, user_id="u1", rating=5)
    add_review(app_id=app, user_id="u2", rating=3)
    s = get_rating_summary(app)
    assert s["average"] == 4.0
    assert s["count"] == 2
    assert s["distribution"][5] == 1

def test_empty_summary():
    s = get_rating_summary("no-reviews")
    assert s["count"] == 0
    assert s["average"] == 0
