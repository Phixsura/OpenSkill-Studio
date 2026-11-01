from app.services.app_marketplace_app_quick_action import get_available_actions, execute_action

def test_owner_actions():
    r = get_available_actions(app_status="running", user_role="owner")
    assert r["total"] == 8
    assert any(a["id"] == "delete" for a in r["actions"])

def test_viewer_no_delete():
    r = get_available_actions(app_status="running", user_role="viewer")
    assert not any(a["id"] == "delete" for a in r["actions"])

def test_paused():
    r = get_available_actions(app_status="paused", user_role="owner")
    assert not any(a["id"] == "pause" for a in r["actions"])

def test_execute():
    r = execute_action(action_id="restart")
    assert r["executed"]

def test_execute_needs_confirm():
    r = execute_action(action_id="delete")
    assert "requires_confirm" in r

def test_execute_confirmed():
    r = execute_action(action_id="delete", confirmed=True)
    assert r["executed"]
