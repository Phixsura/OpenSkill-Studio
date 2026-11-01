from app.services.app_marketplace_review_reply import create_reply, get_reply_stats, get_unreplied_reviews

def test_reply():
    r = create_reply(review_id="r1", developer_id="d1", body="Thank you for your feedback!")
    assert r["error"] is None

def test_too_short():
    r = create_reply(review_id="r1", developer_id="d1", body="Thanks")
    assert r["error"]

def test_stats():
    reviews = [{"has_reply": True}, {"has_reply": False}, {"has_reply": True}]
    s = get_reply_stats(reviews=reviews)
    assert s["replied"] == 2
    assert s["reply_rate"] > 60

def test_unreplied():
    reviews = [{"id": "r1", "has_reply": False, "rating": 2, "created_at": "2026-01-01"},
               {"id": "r2", "has_reply": True, "rating": 5, "created_at": "2026-06-01"},
               {"id": "r3", "has_reply": False, "rating": 1, "created_at": "2026-03-01"}]
    r = get_unreplied_reviews(reviews=reviews, sort_by="lowest_rating")
    assert r[0]["rating"] == 1
