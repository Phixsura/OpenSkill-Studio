from app.services.app_marketplace_confirmation_dialog import get_confirmation

def test_uninstall():
    c = get_confirmation(action="uninstall")
    assert c["danger"]
    assert c["title"] == "Uninstall App"
    assert not c["requires_typing"]

def test_delete():
    c = get_confirmation(action="delete_app")
    assert c["requires_typing"]
    assert c["typing_text"] == "DELETE"

def test_deploy():
    c = get_confirmation(action="deploy")
    assert not c["danger"]

def test_unknown():
    c = get_confirmation(action="custom_action")
    assert c["title"] == "Confirm"
