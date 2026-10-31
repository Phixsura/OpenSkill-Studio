from app.services.app_marketplace_quick_actions import get_app_quick_actions, get_installation_quick_actions

def test_draft_actions():
    actions = get_app_quick_actions(app={"id": "a1", "status": "draft"}, user_role="owner")
    ids = [a["id"] for a in actions]
    assert "edit" in ids
    assert "submit" in ids
    assert "settings" in ids

def test_published_actions():
    actions = get_app_quick_actions(app={"id": "a1", "status": "published"}, user_role="developer")
    ids = [a["id"] for a in actions]
    assert "analytics" in ids
    assert "settings" not in ids  # developer can't access settings

def test_install_actions():
    actions = get_installation_quick_actions(installation={"id": "i1"})
    ids = [a["id"] for a in actions]
    assert "configure" in ids
    assert "uninstall" in ids

def test_update_available():
    actions = get_installation_quick_actions(installation={"id": "i1", "update_available": True})
    assert actions[0]["id"] == "update"
