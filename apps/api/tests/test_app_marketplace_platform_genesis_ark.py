from app.services.app_marketplace_platform_genesis_ark import get_genesis_ark
def test_genesis_ark():
    r = get_genesis_ark()
    assert r["worlds_seeded"] > 4000
    assert r["famine"].startswith("IMPOSSIBLE")
    assert len(r["cargo"]) == 3
    assert r["seeds_planted"] > 900000
    assert "NEVER STOPS" in r["status"]
