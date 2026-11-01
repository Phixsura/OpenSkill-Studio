from app.services.app_marketplace_app_app_app_app_app_app_app_onboard_flow import create_flow, complete_step, skip_step

def test_flow():
    f = create_flow([
        {"title": "Create Account", "required": True},
        {"title": "Set Up Profile", "required": True},
        {"title": "Invite Team", "required": False},
    ])
    assert f["total"] == 3
    r = complete_step(f, 0)
    assert r["progress_pct"] == 33
    complete_step(f, 1)
    assert not complete_step(f, 1)["flow_complete"]  # step 2 pending
    r3 = complete_step(f, 2)
    assert r3["flow_complete"]

def test_skip():
    f = create_flow([{"title": "Required", "required": True}, {"title": "Optional", "required": False}])
    assert skip_step(f, 0)["error"] == "cannot_skip_required"
    assert skip_step(f, 1)["skipped"]
