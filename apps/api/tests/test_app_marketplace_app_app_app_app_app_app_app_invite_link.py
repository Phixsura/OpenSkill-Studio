from app.services.app_marketplace_app_app_app_app_app_app_app_invite_link import InviteLinkManager

def test_invite_lifecycle():
    mgr = InviteLinkManager()
    link = mgr.create(org_id="org1", role="admin", max_uses=2)
    assert "code" in link
    v = mgr.validate(link["code"])
    assert v["valid"]
    assert v["role"] == "admin"
    r = mgr.redeem(link["code"])
    assert r["redeemed"]
    assert r["uses"] == 1
    mgr.redeem(link["code"])
    v2 = mgr.validate(link["code"])
    assert not v2["valid"]
    assert v2["reason"] == "max_uses_reached"

def test_revoke():
    mgr = InviteLinkManager()
    link = mgr.create(org_id="org2")
    mgr.revoke(link["code"])
    v = mgr.validate(link["code"])
    assert not v["valid"]
    assert v["reason"] == "expired"
