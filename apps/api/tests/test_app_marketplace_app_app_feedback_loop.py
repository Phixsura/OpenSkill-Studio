from app.services.app_marketplace_app_app_feedback_loop import submit_feedback, update_status, get_feedback_board

def test_submit():
    r = submit_feedback(user_id="u1", app_id="a1", category="feature",
        title="Add dark mode", description="Please add dark mode support")
    assert r["feedback_id"].startswith("fb_")
    assert r["status"] == "open"

def test_invalid_cat():
    r = submit_feedback(user_id="u1", app_id="a1", category="rant",
        title="X", description="Y")
    assert "error" in r

def test_update():
    r = update_status(feedback_id="fb_1", status="planned", developer_note="Coming in v3!")
    assert r["updated"]
    assert r["status"] == "planned"

def test_board():
    items = [{"status": "open", "votes": 10}, {"status": "open", "votes": 5},
             {"status": "shipped", "votes": 20}]
    r = get_feedback_board(items=items)
    assert r["open_count"] == 2
    assert r["columns"]["open"][0]["votes"] == 10  # sorted by votes
