from app.services.app_marketplace_app_accessibility_audit import run_audit

def test_full_pass():
    results = {r: True for r in ["color-contrast", "alt-text", "keyboard-nav", "focus-visible",
               "heading-order", "aria-labels", "form-labels", "skip-link"]}
    r = run_audit(results=results)
    assert r["score"] == 100
    assert r["wcag_aa_compliant"]
    assert r["grade"] == "A"

def test_partial():
    results = {"alt-text": True, "keyboard-nav": True, "heading-order": True,
               "aria-labels": True, "form-labels": True}
    r = run_audit(results=results)
    assert not r["wcag_aa_compliant"]
    assert r["grade"] == "B"  # A-level all pass

def test_fail():
    r = run_audit(results={})
    assert r["score"] == 0
    assert r["grade"] == "F"
