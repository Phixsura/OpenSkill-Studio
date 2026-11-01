from app.services.app_marketplace_app_app_app_review import create_review, build_review_summary

def test_create():
    r = create_review(app_id="a1", user_id="u1", rating=5, title="Great!", body="Love it")
    assert r["id"].startswith("rev_")
    assert r["rating"] == 5

def test_invalid_rating():
    r = create_review(app_id="a1", user_id="u1", rating=6, title="X", body="Y")
    assert "error" in r

def test_summary():
    reviews = [{"rating": 5, "created_at": "2026-01-03"}, {"rating": 4, "created_at": "2026-01-02"},
               {"rating": 3, "created_at": "2026-01-01"}]
    r = build_review_summary(reviews=reviews)
    assert r["avg_rating"] == 4.0
    assert r["total"] == 3
    assert r["distribution"][5] == 1
