from app.services.app_marketplace_app_app_install_button import build_install_button

def test_free():
    r = build_install_button(installed=False, price=0, permissions_count=3)
    assert r["label"] == "Install Free"
    assert r["action"] == "install"
    assert r["show_permissions"]

def test_paid():
    r = build_install_button(installed=False, price=9.99)
    assert "$9.99" in r["label"]

def test_installed():
    r = build_install_button(installed=True)
    assert r["variant"] == "installed"
    assert r["secondary_action"] == "uninstall"

def test_installing():
    r = build_install_button(installed=False, installing=True)
    assert r["variant"] == "loading"
    assert r["disabled"]
