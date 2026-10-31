from app.services.app_marketplace_app_app_app_app_app_app_app_permission_policy import PermissionPolicyEngine

def test_policy():
    e = PermissionPolicyEngine()
    e.add_policy(name="admin_all", effect="allow", resource="*", actions=["*"],
                  conditions={"role": "admin"})
    e.add_policy(name="member_read", effect="allow", resource="apps/*",
                  actions=["read", "list"])
    e.add_policy(name="deny_delete", effect="deny", resource="apps/*",
                  actions=["delete"], conditions={"role": "member"})
    r1 = e.evaluate(resource="apps/123", action="read")
    assert r1["allowed"]
    r2 = e.evaluate(resource="apps/123", action="delete", context={"role": "member"})
    assert not r2["allowed"]
    assert r2["reason"] == "denied"
    r3 = e.evaluate(resource="billing", action="read", context={"role": "admin"})
    assert r3["allowed"]
    r4 = e.evaluate(resource="billing", action="read")
    assert not r4["allowed"]
