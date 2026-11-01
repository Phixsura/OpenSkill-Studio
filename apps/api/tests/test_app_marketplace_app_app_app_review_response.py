from app.services.app_marketplace_app_app_app_review_response import create_response, build_review_with_response

def test_create():
    r = create_response(review_id="r1", developer_id="d1", body="Thank you for your feedback! We appreciate it.")
    assert r["id"].startswith("resp_")

def test_too_short():
    r = create_response(review_id="r1", developer_id="d1", body="Thanks")
    assert "error" in r

def test_review_with_response():
    r = build_review_with_response(
        review={"rating": 4, "title": "Good app", "body": "Works well", "author": "Alice"},
        response={"body": "Thank you!", "created_at": "2026-01-02"})
    assert r["has_response"]
    assert r["review"]["rating"] == 4
    assert r["response"]["body"] == "Thank you!"

def test_no_response():
    r = build_review_with_response(review={"rating": 3, "title": "OK"})
    assert not r["has_response"]
