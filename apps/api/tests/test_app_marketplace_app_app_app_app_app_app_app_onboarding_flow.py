from app.services.app_marketplace_app_app_app_app_app_app_app_onboarding_flow import create_onboarding, complete_step

def test_onboarding():
    ob = create_onboarding(user_id="alice", plan="pro")
    assert ob["total"] == 6
    assert ob["progress_pct"] == 0
    r1 = complete_step(ob, "profile")
    assert r1["completed_count"] == 1
    assert r1["progress_pct"] == 17
    assert r1["next_step"] == "create_app"
    for sid in ["create_app", "api_key", "first_request", "webhook", "invite_team"]:
        complete_step(ob, sid)
    assert ob["progress_pct"] == 100
