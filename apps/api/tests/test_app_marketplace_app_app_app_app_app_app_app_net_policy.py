from app.services.app_marketplace_app_app_app_app_app_app_app_net_policy import NetworkPolicyManager

def test_allow():
    npm = NetworkPolicyManager()
    npm.add_policy("web-to-api", "web", "api", 8080)
    r = npm.evaluate("web", "api", 8080)
    assert r["allowed"]
    assert r["matched_policy"] == "web-to-api"

def test_deny():
    npm = NetworkPolicyManager()
    npm.add_policy("block-external", "external", "db", 5432, action="deny")
    r = npm.evaluate("external", "db", 5432)
    assert not r["allowed"]

def test_implicit_deny():
    npm = NetworkPolicyManager()
    r = npm.evaluate("unknown", "api", 8080)
    assert not r["allowed"]
    assert r["action"] == "implicit_deny"
