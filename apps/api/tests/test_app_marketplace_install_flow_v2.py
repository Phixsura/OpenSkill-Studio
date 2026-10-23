from app.services.app_marketplace_install_flow_v2 import build_install_flow, advance_install_step

def test_flow():
    f = build_install_flow(app={"id": "a1", "name": "App", "required_scopes": ["read"], "config_fields": [{"name": "url"}]},
                             org={"name": "Acme"}, existing_installs=[])
    assert f["can_proceed"]
    assert f["step_count"] == 3

def test_already_installed():
    f = build_install_flow(app={"id": "a1", "name": "App"}, org={},
                             existing_installs=[{"app_id": "a1", "status": "active"}])
    assert not f["can_proceed"]

def test_advance():
    flow = {"steps": [{"key": "permissions", "status": "pending"}, {"key": "confirm", "status": "pending"}]}
    r = advance_install_step(flow=flow, step_key="permissions")
    assert r["steps"][0]["status"] == "completed"
    assert not r["ready_to_install"]
    r = advance_install_step(flow=r, step_key="confirm")
    assert r["ready_to_install"]
