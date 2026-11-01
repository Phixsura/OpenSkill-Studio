from app.services.app_marketplace_app_app_app_install_button import build_install_button

def test_free_install():
    r = build_install_button(app={"pricing": "Free"})
    assert r["state"] == "install"
    assert "Free" in r["label"]

def test_already_installed():
    r = build_install_button(app={"pricing": "Free"}, user_installed=True)
    assert r["state"] == "installed"
    assert r["disabled"]

def test_paid():
    r = build_install_button(app={"pricing": "$9/mo"})
    assert r["state"] == "subscribe"
    assert "$9/mo" in r["label"]

def test_upgrade_required():
    r = build_install_button(app={"pricing": "Free", "min_plan": "pro"}, user_plan="free")
    assert r["state"] == "upgrade_required"
    assert r["action"] == "upgrade"
