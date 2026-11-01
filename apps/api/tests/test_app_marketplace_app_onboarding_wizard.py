from app.services.app_marketplace_app_onboarding_wizard import get_wizard_state

def test_partial():
    r = get_wizard_state(completed_steps=["name", "description"])
    assert r["completed"] == 2
    assert r["current_step"] == "category"
    assert not r["can_submit"]

def test_all_required():
    required = ["name", "description", "category", "icon", "pricing", "review"]
    r = get_wizard_state(completed_steps=required)
    assert r["can_submit"]

def test_empty():
    r = get_wizard_state(completed_steps=[])
    assert r["progress_pct"] == 0
    assert r["current_step"] == "name"
