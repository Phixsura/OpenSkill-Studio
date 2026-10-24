from app.services.app_marketplace_app_app_app_app_app_app_app_cli_tool_mgr import list_tools, check_tool, install_report

def test_list():
    r = list_tools([
        {"name": "node", "installed": True, "update_available": False},
        {"name": "docker", "installed": True, "update_available": True},
        {"name": "kubectl", "installed": False, "update_available": False},
    ])
    assert r["installed"] == 2
    assert r["outdated"] == 1

def test_check():
    r = check_tool("node", "18.0.0", "20.0.0")
    assert r["update_available"]
    assert r["major_update"]

def test_report():
    r = install_report([{"action": "install", "status": "ok"}, {"action": "update", "status": "ok"}])
    assert r["success"]
    assert r["installed"] == 1
