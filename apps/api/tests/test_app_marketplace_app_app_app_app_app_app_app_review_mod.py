from app.services.app_marketplace_app_app_app_app_app_app_app_review_mod import moderate_review, moderation_stats

def test_approved():
    r = moderate_review({"body": "Great app, works perfectly!", "rating": 5})
    assert r["status"] == "approved"
    assert len(r["flags"]) == 0

def test_rejected():
    r = moderate_review({"body": "This is spam and a scam!", "rating": 1})
    assert r["status"] == "rejected"

def test_flagged():
    r = moderate_review({"body": "Meh", "rating": 3})
    assert r["status"] == "flagged"
    assert "too_short" in r["flags"]

def test_stats():
    reviews = [
        {"body": "Great app, love it!", "rating": 5},
        {"body": "OK", "rating": 3},
        {"body": "This is spam", "rating": 1},
    ]
    s = moderation_stats(reviews)
    assert s["total"] == 3
    assert s["by_status"]["approved"] == 1
