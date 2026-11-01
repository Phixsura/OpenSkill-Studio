from app.services.app_marketplace_platform_atlas import get_atlas
def test_atlas():
    r = get_atlas()
    assert len(r["territories"]) == 3
    assert r["unexplored"] == 0
    assert "1:1" in r["scale"]
    assert r["routes_charted"] > 4000
    assert "NEVER STOPS" in r["status"]
