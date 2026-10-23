from app.services.app_marketplace_complete_onboarding_flow import build_onboarding_flow, get_onboarding_tips

def test_empty():
    f = build_onboarding_flow(completed_steps=[])
    assert f["progress_pct"] == 0
    assert f["current_step"]["key"] == "welcome"
    assert not f["required_complete"]

def test_partial():
    f = build_onboarding_flow(completed_steps=["welcome", "profile"])
    assert f["completed"] == 2
    assert f["current_step"]["key"] == "first_app"
    assert f["progress_pct"] == 33

def test_all_required():
    required = ["welcome", "profile", "first_app", "manifest", "submit"]
    f = build_onboarding_flow(completed_steps=required)
    assert f["required_complete"]
    assert f["can_skip_to_publish"]

def test_tips():
    t = get_onboarding_tips(current_step="manifest")
    assert any("validator" in tip for tip in t)
