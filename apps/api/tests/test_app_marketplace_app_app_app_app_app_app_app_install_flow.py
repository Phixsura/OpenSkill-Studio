from app.services.app_marketplace_app_app_app_app_app_app_app_install_flow import build_install_flow, advance_step

def test_flow():
    f = build_install_flow({"name": "Slack Bot", "icon": "💬", "developer": "Acme",
                              "version": "2.0", "permissions": [
                                  {"name": "read:profile", "description": "Read your profile", "risk": "low"},
                                  {"name": "deploy", "description": "Deploy apps", "risk": "high"},
                              ]})
    assert f["app_name"] == "Slack Bot"
    assert f["total_steps"] == 4
    assert f["has_dangerous_permissions"]
    assert len(f["permissions"]) == 2

def test_advance():
    f = build_install_flow({"name": "Test", "permissions": []})
    r = advance_step(f, 0)
    assert r["progress"] == "1/4"
    assert not r["done"]
    advance_step(f, 1)
    advance_step(f, 2)
    r4 = advance_step(f, 3)
    assert r4["done"]
