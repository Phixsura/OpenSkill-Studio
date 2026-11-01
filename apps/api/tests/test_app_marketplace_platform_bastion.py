from app.services.app_marketplace_platform_bastion import get_bastion
def test_bastion():
    r = get_bastion()
    assert r["attacks_repelled"] == 0
    assert r["morale"] == "MAXIMUM — the garrison is proud"
    assert r["fortifications"] > 4000
    assert "TRIPLE" in r["redundancy_level"]
    assert "NEVER STOPS" in r["status"]
