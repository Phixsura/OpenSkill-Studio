from app.services.app_marketplace_review_form import validate_review, build_review_preview, get_review_guidelines

def test_valid():
    r = validate_review(rating=5, title="Great app!", body="This is a fantastic tool that saved me hours of work.",
                          pros=["Fast"], cons=["None"])
    assert r["valid"]

def test_invalid_rating():
    r = validate_review(rating=6, title="Good app title here", body="A" * 25, pros=[], cons=[])
    assert not r["valid"]

def test_short_body():
    r = validate_review(rating=4, title="Title here", body="Short", pros=[], cons=[])
    assert not r["valid"]

def test_profanity():
    r = validate_review(rating=1, title="This is a scam", body="Total spam app waste of time and money here.",
                          pros=[], cons=[])
    assert not r["valid"]
    assert len(r["flagged_words"]) > 0

def test_preview():
    p = build_review_preview(rating=5, title="Great!", body="Love it so much", pros=["Fast"], cons=[], author_name="Alice")
    assert p["stars"] == "★★★★★"
    assert p["author"] == "Alice"

def test_guidelines():
    g = get_review_guidelines()
    assert len(g) >= 5
