from app.services.app_marketplace_app_app_app_app_app_app_app_app_perms import check_permissions, classify_risk

def test_check():
    r = check_permissions(requested=["read:profile", "write:apps", "deploy"],
                           granted=["read:profile", "read:apps", "deploy"])
    assert not r["all_granted"]
    assert "write:apps" in r["denied"]
    assert len(r["allowed"]) == 2

def test_all_granted():
    r = check_permissions(requested=["read:profile"], granted=["read:profile", "read:apps"])
    assert r["all_granted"]

def test_risk():
    r = classify_risk(["read:profile", "write:apps", "admin:org"])
    assert r["max_risk"] == "critical"
    assert r["risks"]["critical"] == 1
    assert r["risks"]["high"] == 1
