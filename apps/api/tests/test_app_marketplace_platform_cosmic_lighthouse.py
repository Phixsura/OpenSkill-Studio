from app.services.app_marketplace_platform_cosmic_lighthouse import get_cosmic_lighthouse
def test_cosmic_lighthouse():
    r = get_cosmic_lighthouse()
    assert r["beams"] > 4000
    assert r["ships_lost"] == 0
    assert "GREEN" in r["beam_type"]
    assert r["fog"].startswith("PENETRATED")
    assert "NEVER STOPS" in r["status"]
