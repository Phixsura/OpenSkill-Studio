from app.services.app_marketplace_platform_archon import get_archon
def test_archon():
    r = get_archon()
    assert r["decrees"] > 4000
    assert r["rebellion"].startswith("ZERO")
    assert r["justice"].startswith("ABSOLUTE")
    assert len(r["treasury"]) == 3
    assert "NEVER STOPS" in r["status"]
