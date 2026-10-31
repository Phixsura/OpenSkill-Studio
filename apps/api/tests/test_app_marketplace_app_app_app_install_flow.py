from app.services.app_marketplace_app_app_app_install_flow import start_install, complete_install

def test_start():
    r = start_install(app_id="app1", app_name="SuperApp", permissions=["read:data", "write:config"])
    assert r["install_id"].startswith("inst_")
    assert r["total_steps"] == 4
    assert r["current_step"] == 0
    assert len(r["permissions"]) == 2

def test_complete():
    r = complete_install(install_id="inst_abc", app_id="app1")
    assert r["status"] == "installed"
    assert "🎉" in r["message"]
