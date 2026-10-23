from app.services.app_marketplace_app_app_app_submission import create_submission, evaluate_checklist

def test_create():
    r = create_submission(app_id="a1", version="2.0.0", notes="Major release")
    assert r["submission_id"].startswith("sub_")
    assert r["status"] == "pending_review"
    assert len(r["checklist"]) == 6

def test_checklist_pass():
    results = {c["id"]: True for c in [{"id": "manifest"}, {"id": "security"}, {"id": "docs"},
                                         {"id": "screenshots"}, {"id": "privacy"}, {"id": "testing"}]}
    r = evaluate_checklist(results=results)
    assert r["ready_for_review"]
    assert r["score"] == 100

def test_checklist_fail():
    r = evaluate_checklist(results={"manifest": True, "security": True})
    assert not r["ready_for_review"]
    assert r["passed"] == 2
