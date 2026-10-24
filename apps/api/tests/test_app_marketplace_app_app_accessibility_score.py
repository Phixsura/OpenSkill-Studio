from app.services.app_marketplace_app_app_accessibility_score import calculate_a11y_score

def test_perfect():
    results = {c: True for c in ["alt_text", "color_contrast", "keyboard_nav", "focus_visible",
               "form_labels", "error_messages", "semantic_html", "aria_roles"]}
    r = calculate_a11y_score(results=results)
    assert r["score"] == 100
    assert r["grade"] == "A"

def test_partial():
    results = {"alt_text": True, "keyboard_nav": True, "form_labels": True}
    r = calculate_a11y_score(results=results)
    assert r["grade"] in ("B", "C")
    assert r["passed"] == 3

def test_none():
    r = calculate_a11y_score(results={})
    assert r["score"] == 0
    assert r["grade"] == "F"
