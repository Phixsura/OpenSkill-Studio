from app.services.app_marketplace_app_app_review_card_display import format_review_card

def test_format():
    review = {"review_id": "r1", "author": "Alice Smith", "rating": 5,
              "title": "Amazing SDK!", "body": "Best auth solution I've used.",
              "helpful_count": 12, "created_at": "2026-10-23T12:00:00"}
    r = format_review_card(review=review)
    assert r["author"] == "Alice Smith"
    assert r["avatar_initials"] == "AS"
    assert r["stars"] == "★★★★★"
    assert r["helpful_count"] == 12
    assert r["date_display"] == "2026-10-23"
    assert not r["has_response"]

def test_with_response():
    review = {"author": "Bob", "rating": 3, "title": "OK", "body": "Decent app.",
              "developer_response": "Thanks for feedback!"}
    r = format_review_card(review=review)
    assert r["has_response"]
    assert r["developer_response"] == "Thanks for feedback!"

def test_xss():
    review = {"author": "<script>", "title": "<b>bold</b>", "body": "ok", "rating": 4}
    r = format_review_card(review=review)
    assert "<script>" not in r["author"]
    assert "<b>" not in r["title"]
