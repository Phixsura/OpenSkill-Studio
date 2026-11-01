from app.services.app_marketplace_app_app_install_flow import start_install, complete_step

def test_start():
    r = start_install(app_id="a1", app_name="Auth SDK", user_id="u1",
        permissions=["read:profile", "write:data"])
    assert r["install_id"].startswith("inst_")
    assert r["status"] == "in_progress"
    assert len(r["steps"]) == 4
    assert r["steps"][0]["status"] == "current"

def test_complete_step():
    inst = start_install(app_id="a1", app_name="X", user_id="u1", permissions=[])
    r = complete_step(install=inst, step_id="review_permissions")
    assert r["steps"][0]["status"] == "completed"
    assert r["steps"][1]["status"] == "current"

def test_all_complete():
    inst = start_install(app_id="a1", app_name="X", user_id="u1", permissions=[])
    for sid in ["review_permissions", "configure", "connect", "complete"]:
        inst = complete_step(install=inst, step_id=sid)
    assert inst["status"] == "completed"
