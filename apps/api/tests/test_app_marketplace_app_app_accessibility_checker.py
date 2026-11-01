from app.services.app_marketplace_app_app_accessibility_checker import run_audit

def test_all_pass():
    checks = [{"id": "alt_text", "pass": True}, {"id": "label", "pass": True}]
    r = run_audit(checks=checks)
    assert r["score"] == 100
    assert r["grade"] == "A"
    assert r["failed"] == 0

def test_mixed():
    checks = [
        {"id": "alt_text", "pass": True},
        {"id": "color_contrast", "pass": False, "details": "Ratio 3.5:1 below 4.5:1"},
        {"id": "label", "pass": True},
    ]
    r = run_audit(checks=checks)
    assert r["passed"] == 2
    assert r["failed"] == 1
    assert r["score"] == 67
    assert r["grade"] == "C"
