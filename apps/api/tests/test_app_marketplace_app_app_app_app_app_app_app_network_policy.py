from app.services.app_marketplace_app_app_app_app_app_app_app_network_policy import NetworkPolicyManager

def test_policy():
    mgr = NetworkPolicyManager()
    mgr.create_policy("api-policy", target="api",
                       ingress=[{"from": "gateway", "ports": [8080]},
                                {"from": "monitoring", "ports": [9090]}],
                       egress=[{"to": "database", "ports": [5432]}])
    r = mgr.check_allowed(source="gateway", destination="api", port=8080)
    assert r["allowed"]
    r2 = mgr.check_allowed(source="unknown", destination="api", port=8080)
    assert not r2["allowed"]
    r3 = mgr.check_allowed(source="api", destination="database", port=5432)
    assert r3["allowed"]
    s = mgr.summary()
    assert s["total_policies"] == 1
    assert s["total_rules"] == 3
