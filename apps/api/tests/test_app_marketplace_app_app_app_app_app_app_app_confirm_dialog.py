from app.services.app_marketplace_app_app_app_app_app_app_app_confirm_dialog import build_dialog

def test_delete():
    r = build_dialog("delete_app", resource_name="My App")
    assert r["title"] == "Delete App?"
    assert "My App" in r["body"]
    assert r["variant"] == "danger"
    assert r["confirm_label"] == "Delete"

def test_deploy():
    r = build_dialog("deploy_prod")
    assert r["variant"] == "primary"
    assert r["confirm_label"] == "Deploy"

def test_unknown():
    r = build_dialog("unknown_action")
    assert "error" in r
