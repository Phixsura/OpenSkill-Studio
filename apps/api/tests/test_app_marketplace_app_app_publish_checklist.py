from app.services.app_marketplace_app_app_publish_checklist import evaluate_checklist

def test_ready():
    results = {i: True for i in ["manifest", "icon", "screenshots", "description",
               "privacy", "tests", "security", "perf", "changelog", "docs"]}
    r = evaluate_checklist(results=results)
    assert r["can_publish"]
    assert r["readiness_pct"] == 100
    assert len(r["blocking"]) == 0

def test_missing_required():
    results = {"manifest": True, "icon": False, "screenshots": True, "description": True, "privacy": False}
    r = evaluate_checklist(results=results)
    assert not r["can_publish"]
    assert len(r["blocking"]) >= 2

def test_optional_missing():
    results = {"manifest": True, "icon": True, "screenshots": True, "description": True,
               "privacy": True, "tests": True, "security": True}
    r = evaluate_checklist(results=results)
    assert r["can_publish"]  # required all pass
