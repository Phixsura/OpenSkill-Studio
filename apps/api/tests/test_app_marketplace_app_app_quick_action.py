from app.services.app_marketplace_app_app_quick_action import get_actions

def test_app_actions():
    r = get_actions(context="app", resource_id="a1")
    assert r["total"] == 5
    assert r["actions"][0]["label"] == "Edit App"
    assert r["actions"][-1]["danger"]

def test_webhook_actions():
    r = get_actions(context="webhook")
    assert r["total"] == 4

def test_unknown():
    r = get_actions(context="unknown")
    assert r["total"] == 0
