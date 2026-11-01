from app.services.app_marketplace_platform_armada import get_armada
def test_armada():
    r = get_armada()
    assert r["ships_lost"] == 0
    assert r["cargo_delivered"].startswith("100%")
    assert r["voyages"] > 4000
    assert "DORA Elite" in r["flagship"]
    assert "NEVER STOPS" in r["status"]
