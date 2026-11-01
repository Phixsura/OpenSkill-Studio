from app.services.app_review_checklist import create_review_checklist, is_review_complete, get_review_summary, REVIEW_CRITERIA

def test_create_empty():
    cl = create_review_checklist()
    assert len(cl) == len(REVIEW_CRITERIA)
    assert all(not i["checked"] for i in cl)

def test_create_with_auto():
    auto = {"manifest": {"passed": True, "message": "Valid"}, "security": {"passed": True, "message": "No issues"}}
    cl = create_review_checklist(auto_results=auto)
    manifest = next(i for i in cl if i["id"] == "manifest")
    assert manifest["checked"] is True

def test_not_complete():
    cl = create_review_checklist()
    assert is_review_complete(cl) is False

def test_complete():
    cl = create_review_checklist()
    for item in cl:
        item["checked"] = True
    assert is_review_complete(cl) is True

def test_summary():
    cl = create_review_checklist()
    cl[0]["checked"] = True
    s = get_review_summary(cl)
    assert s["checked"] == 1
    assert s["remaining"] == len(REVIEW_CRITERIA) - 1
    assert not s["complete"]

def test_criteria_count():
    assert len(REVIEW_CRITERIA) >= 7
