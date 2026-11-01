from app.services.app_developer_feedback import submit_feedback, get_feedback_stats

def test_submit():
    f = submit_feedback(developer_id="d1", feedback_type="bug", message="Button broken", page="/apps")
    assert f is not None
    assert f["status"] == "open"

def test_invalid_type():
    assert submit_feedback(developer_id="d1", feedback_type="invalid", message="x") is None

def test_stats():
    submit_feedback(developer_id="d2", feedback_type="feature_request", message="Add dark mode")
    s = get_feedback_stats()
    assert s["total"] >= 1
    assert s["open"] >= 1
