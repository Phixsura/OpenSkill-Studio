from app.services.app_marketplace_app_app_app_app_app_app_app_cors_policy import CorsPolicyManager

def test_allow():
    cm = CorsPolicyManager()
    cm.set_policy("https://app.example.com", methods=["GET", "POST"])
    r = cm.check("https://app.example.com", "GET")
    assert r["allowed"]

def test_deny_origin():
    cm = CorsPolicyManager()
    cm.set_policy("https://allowed.com")
    r = cm.check("https://evil.com", "GET")
    assert not r["allowed"]

def test_wildcard():
    cm = CorsPolicyManager()
    cm.set_policy("*")
    r = cm.check("https://anything.com", "GET")
    assert r["allowed"]

def test_method_denied():
    cm = CorsPolicyManager()
    cm.set_policy("https://app.com", methods=["GET"])
    r = cm.check("https://app.com", "DELETE")
    assert not r["allowed"]
