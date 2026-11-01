from app.services.app_marketplace_app_app_review_form import validate_review

def test_valid():
    r = validate_review(rating=5, title="Great authentication SDK!",
        body="This SDK made auth integration so easy. Highly recommend for any project.",
        user_id="u1")
    assert r["valid"]
    assert r["review"]["rating"] == 5
    assert r["review"]["review_id"].startswith("rev_")

def test_invalid_rating():
    r = validate_review(rating=0, title="Hello World", body="x" * 20, user_id="u1")
    assert not r["valid"]
    assert any("Rating" in e for e in r["errors"])

def test_short_body():
    r = validate_review(rating=4, title="Good app", body="Short", user_id="u1")
    assert not r["valid"]

def test_xss():
    r = validate_review(rating=5, title="<script>xss</script> Great!",
        body="Amazing app that works perfectly for our team!", user_id="u1")
    assert r["valid"]
    assert "<script>" not in r["review"]["title"]
