from app.services.app_marketplace_app_app_app_app_app_app_app_onboarding_progress import compute_progress, get_congratulations

def test_progress():
    r = compute_progress(["profile", "first_app", "api_key"])
    assert r["completed_count"] == 3
    assert r["progress_pct"] > 0
    assert not r["finished"]
    assert r["next_step"]["id"] == "first_call"

def test_complete():
    all_ids = ["profile", "first_app", "api_key", "first_call", "webhook", "invite", "deploy"]
    r = compute_progress(all_ids)
    assert r["finished"]
    assert r["progress_pct"] == 100
    msg = get_congratulations(r)
    assert "Congratulations" in msg
