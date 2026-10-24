from app.services.app_marketplace_onboarding_progress import get_onboarding_progress, unlock_achievement

def test_empty():
    r = get_onboarding_progress(completed=[])
    assert r["progress_pct"] == 0
    assert r["next_step"]["id"] == "account"
    assert not r["all_complete"]

def test_partial():
    r = get_onboarding_progress(completed=["account", "profile", "first_app"])
    assert r["completed_count"] == 3
    assert r["progress_pct"] > 0
    assert r["next_step"]["id"] == "manifest"

def test_all_complete():
    all_ids = [m["id"] for m in [{"id": "account"}, {"id": "profile"}, {"id": "first_app"}, {"id": "manifest"},
               {"id": "first_test"}, {"id": "submit_review"}, {"id": "first_install"}, {"id": "first_review"}]]
    r = get_onboarding_progress(completed=all_ids)
    assert r["all_complete"]
    assert r["progress_pct"] == 100

def test_unlock():
    r = unlock_achievement(milestone_id="first_app")
    assert r["points"] == 25
    assert "unlocked" in r["message"]

def test_unlock_invalid():
    assert unlock_achievement(milestone_id="nonexistent") is None
