from app.services.app_marketplace_platform_world_tree import get_world_tree
def test_world_tree():
    r = get_world_tree()
    assert r["seasons"] > 4000
    assert r["leaves"] > 900000
    assert len(r["nine_realms"]) == 3
    assert r["nidhogg"].startswith("DEFEATED")
    assert "NEVER STOPS" in r["status"]
