from app.services.app_marketplace_developer_onboarding import get_onboarding_status, get_onboarding_tips

def test_empty():
    s = get_onboarding_status(completed_steps=[])
    assert s["progress_pct"] == 0
    assert not s["can_publish"]
    assert s["next_step"] == "profile"

def test_partial():
    s = get_onboarding_status(completed_steps=["profile", "agreement"])
    assert s["progress_pct"] == 25
    assert not s["can_publish"]

def test_all_required():
    s = get_onboarding_status(completed_steps=["profile", "agreement", "first_app", "manifest", "version"])
    assert s["can_publish"]
    assert s["next_step"] == "webhook"

def test_all_done():
    all_keys = ["profile", "agreement", "first_app", "manifest", "version", "webhook", "docs", "icon"]
    s = get_onboarding_status(completed_steps=all_keys)
    assert s["progress_pct"] == 100
    assert s["next_step"] is None

def test_tips():
    tips = get_onboarding_tips(next_step="manifest")
    assert any("validator" in t for t in tips)

def test_tips_done():
    tips = get_onboarding_tips(next_step=None)
    assert any("all set" in t for t in tips)
