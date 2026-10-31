from app.services.app_marketplace_app_app_review_response import create_response, get_response_stats

def test_create():
    r = create_response(review_id="r1", developer_id="d1",
        message="Thank you for your feedback! We're working on improvements.")
    assert r["response_id"].startswith("resp_")
    assert r["visible"]

def test_too_short():
    r = create_response(review_id="r1", developer_id="d1", message="Thanks")
    assert "error" in r

def test_xss():
    r = create_response(review_id="r1", developer_id="d1",
        message='<script>alert("xss")</script> We appreciate your review!')
    assert "<script>" not in r["message"]

def test_stats():
    reviews = [
        {"has_response": True, "rating": 5},
        {"has_response": False, "rating": 1},
        {"has_response": True, "rating": 3},
    ]
    r = get_response_stats(reviews=reviews)
    assert r["response_rate"] == 66.7
    assert r["unresponded_negative"] == 1
