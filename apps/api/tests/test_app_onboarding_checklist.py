from app.services.app_onboarding_checklist import generate_checklist, compute_progress

def test_connector():
    cl = generate_checklist("connector")
    assert "Add secrets" in cl

def test_automation():
    cl = generate_checklist("automation")
    assert "Subscribe to events" in cl

def test_progress():
    cl = generate_checklist("connector")
    p = compute_progress(cl, {"Create app", "Add manifest"})
    assert p["done"] == 2
    assert p["pct"] > 0
