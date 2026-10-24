from app.services.app_marketplace_app_app_app_app_app_app_app_quick_actions import list_actions, execute_action

def test_list():
    r = list_actions()
    assert r["total"] == 6
    r2 = list_actions("deployment")
    assert r2["total"] == 3

def test_execute():
    r = execute_action("deploy")
    assert r["executed"]
    r2 = execute_action("unknown")
    assert not r2["executed"]
