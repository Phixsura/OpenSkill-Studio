from app.services.app_review_queue import submit_for_review, get_pending_reviews, assign_reviewer, complete_review, get_queue_stats

def test_submit():
    r = submit_for_review(app_id="rq1", version_id="v1", submitted_by="u1")
    assert r["status"] == "pending"

def test_get_pending():
    submit_for_review(app_id="rq2", version_id="v1", submitted_by="u1")
    pending = get_pending_reviews()
    assert any(r["app_id"] == "rq2" for r in pending)

def test_assign():
    submit_for_review(app_id="rq3", version_id="v1", submitted_by="u1")
    assert assign_reviewer("rq3", "reviewer1") is True

def test_complete():
    submit_for_review(app_id="rq4", version_id="v1", submitted_by="u1")
    assign_reviewer("rq4", "rev1")
    assert complete_review("rq4", decision="approved", notes="Looks good") is True

def test_stats():
    s = get_queue_stats()
    assert s["total"] >= 0
    assert isinstance(s["by_status"], dict)
