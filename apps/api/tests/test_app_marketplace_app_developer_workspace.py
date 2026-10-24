from app.services.app_marketplace_app_developer_workspace import create_workspace, add_app_to_workspace, get_workspace_overview

def test_create():
    w = create_workspace(name="My Workspace", owner_id="u1", apps=["a1", "a2"])
    assert w["app_count"] == 2
    assert "u1" in w["members"]

def test_short_name():
    w = create_workspace(name="ab", owner_id="u1", apps=[])
    assert w["error"]

def test_add_app():
    w = create_workspace(name="MyWS", owner_id="u1", apps=["a1"])
    w = add_app_to_workspace(workspace=w, app_id="a2")
    assert w["app_count"] == 2

def test_add_duplicate():
    w = create_workspace(name="MyWS", owner_id="u1", apps=["a1"])
    w = add_app_to_workspace(workspace=w, app_id="a1")
    assert w["error"]

def test_overview():
    ws = {"name": "WS", "apps": ["a1", "a2"], "members": ["u1"]}
    apps = [{"install_count": 100, "status": "published"}, {"install_count": 50, "status": "draft"}]
    o = get_workspace_overview(workspace=ws, app_details=apps)
    assert o["total_installs"] == 150
    assert o["published_apps"] == 1
