from app.services.app_marketplace_app_accessibility_checker import run_accessibility_audit

def test_full():
    all_ids = [c["id"] for c in [{"id": "color-contrast"}, {"id": "alt-text"}, {"id": "keyboard-nav"},
               {"id": "focus-visible"}, {"id": "aria-labels"}, {"id": "heading-hierarchy"},
               {"id": "form-labels"}, {"id": "error-messages"}]]
    r = run_accessibility_audit(passed_checks=all_ids)
    assert r["score"] == 100
    assert r["wcag_aa_compliant"]

def test_partial():
    r = run_accessibility_audit(passed_checks=["alt-text", "keyboard-nav"])
    assert r["score"] == 25
    assert not r["wcag_a_compliant"]
