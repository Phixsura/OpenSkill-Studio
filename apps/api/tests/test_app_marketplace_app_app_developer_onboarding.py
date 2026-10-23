from app.services.app_marketplace_app_app_developer_onboarding import build_onboarding

def test_fresh():
    r = build_onboarding(completed=[])
    assert r["completed"] == 0
    assert r["progress_pct"] == 0
    assert not r["can_skip_to_dashboard"]
    assert r["next_step"]["id"] == "profile"

def test_required_done():
    r = build_onboarding(completed=["profile", "verify_email", "install_cli"])
    assert r["required_complete"]
    assert r["can_skip_to_dashboard"]

def test_all_done():
    all_ids = ["profile", "verify_email", "create_org", "install_cli", "first_app", "connect_github"]
    r = build_onboarding(completed=all_ids)
    assert r["progress_pct"] == 100
    assert r["next_step"] is None
