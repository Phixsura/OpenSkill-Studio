from app.services.app_marketplace_app_app_app_onboarding_progress import build_setup_progress

def test_partial():
    r = build_setup_progress(completed=["basic_info", "permissions"])
    assert r["completed"] == 2
    assert r["progress_pct"] == 33
    assert not r["ready_to_publish"]
    assert r["next_step"]["id"] == "screenshots"  # next required

def test_ready():
    required = ["basic_info", "permissions", "screenshots", "privacy_policy", "test_install"]
    r = build_setup_progress(completed=required)
    assert r["ready_to_publish"]

def test_all_done():
    all_ids = ["basic_info", "permissions", "webhook_url", "screenshots", "privacy_policy", "test_install"]
    r = build_setup_progress(completed=all_ids)
    assert r["progress_pct"] == 100
    assert r["next_step"] is None
