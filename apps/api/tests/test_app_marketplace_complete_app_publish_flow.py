from app.services.app_marketplace_complete_app_publish_flow import build_publish_flow

def test_ready():
    p = build_publish_flow(app={"id": "a1", "name": "App"}, version={"version": "2.0"},
                              checklist=[], manifest_valid=True, security_clean=True, tests_passed=True)
    assert p["ready_to_publish"]
    assert p["submit_label"] == "Submit for Review"
    assert p["stats"]["pct"] == 100

def test_not_ready():
    p = build_publish_flow(app={"id": "a1", "name": "App"}, version={"version": "1.0"},
                              checklist=[{"key": "docs", "label": "Docs", "passed": False, "required": True}],
                              manifest_valid=True, security_clean=False, tests_passed=True)
    assert not p["ready_to_publish"]
    assert "Complete" in p["submit_label"]
