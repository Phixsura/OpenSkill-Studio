from app.services.app_marketplace_app_app_app_app_app_app_onboarding_complete import build_onboarding_complete

def test_complete():
    r = build_onboarding_complete(user_name="Alice", plan="pro")
    assert "Alice" in r["headline"]
    assert r["plan"] == "pro"
    assert r["step_count"] == 6
    assert r["next_steps"][0]["primary"]
