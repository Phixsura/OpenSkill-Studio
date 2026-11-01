from app.services.app_marketplace_platform_sequoia import get_sequoia
def test_sequoia():
    r = get_sequoia()
    assert r["growth_rings"] > 4000
    assert r["fire_resistance"] == "MAXIMUM — challenges make it stronger"
    assert "engineerium" in r["species"]
    assert "NEVER STOPS" in r["status"]
