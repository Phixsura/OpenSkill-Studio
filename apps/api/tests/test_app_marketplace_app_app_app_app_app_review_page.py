from app.services.app_marketplace_app_app_app_app_app_review_page import build_review_form, submit_review

def test_new_form():
    r = build_review_form(app_name="SuperApp")
    assert r["app_name"] == "SuperApp"
    assert not r["is_edit"]
    assert r["current_rating"] == 0

def test_edit_form():
    r = build_review_form(app_name="X", existing_review={"rating": 4, "title": "Good", "body": "Nice"})
    assert r["is_edit"]
    assert r["current_rating"] == 4

def test_submit():
    r = submit_review(app_id="a1", user_id="u1", rating=5, title="Amazing!", body="Love it")
    assert r["review_id"].startswith("rev_")
    assert r["rating"] == 5

def test_invalid_rating():
    r = submit_review(app_id="a1", user_id="u1", rating=6, title="X", body="Y")
    assert "error" in r
