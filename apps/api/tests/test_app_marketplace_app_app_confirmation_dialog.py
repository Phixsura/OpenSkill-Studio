from app.services.app_marketplace_app_app_confirmation_dialog import get_confirmation

def test_delete():
    r = get_confirmation(action="delete_app")
    assert r["title"] == "Delete App?"
    assert r["danger"]
    assert r["confirm_text"] == "DELETE"

def test_deploy():
    r = get_confirmation(action="deploy_production")
    assert not r["danger"]
    assert r["icon"] == "🚀"

def test_unknown():
    r = get_confirmation(action="launch_missiles")
    assert "error" in r
