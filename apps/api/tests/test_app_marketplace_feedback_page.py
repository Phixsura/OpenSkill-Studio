from app.services.app_marketplace_feedback_page import build_feedback_page, submit_feedback

def test_page():
    p = build_feedback_page(user={"display_name": "Alice"})
    assert p["page_type"] == "feedback"
    assert len(p["categories"]) == 5
    assert p["authenticated"]

def test_anonymous():
    p = build_feedback_page(user=None)
    assert not p["authenticated"]

def test_submit():
    r = submit_feedback(category="bug", title="Button broken", description="The install button doesn't work on mobile devices")
    assert r["success"]
    assert "FB-" in r["ticket_id"]

def test_too_short():
    r = submit_feedback(category="bug", title="Hi", description="Short")
    assert not r["success"]
