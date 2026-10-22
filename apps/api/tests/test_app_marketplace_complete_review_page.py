from app.services.app_marketplace_complete_review_page import build_complete_review_page

def test_ready():
    p = build_complete_review_page(
        app={"id": "a1", "name": "App"}, version={"id": "v1", "version": "1.0"},
        manifest={"valid": True}, security_scan={"vulnerabilities": 0},
        test_results={"pass_rate": 100}, checklist=[{"name": "docs", "passed": True}])
    assert p["ready_to_submit"]
    assert p["page_type"] == "review_submission"

def test_not_ready():
    p = build_complete_review_page(
        app={"id": "a1", "name": "App"}, version={"id": "v1", "version": "1.0"},
        manifest={"valid": True}, security_scan={"vulnerabilities": 3},
        test_results={"pass_rate": 80}, checklist=[{"name": "docs", "passed": False}])
    assert not p["ready_to_submit"]
