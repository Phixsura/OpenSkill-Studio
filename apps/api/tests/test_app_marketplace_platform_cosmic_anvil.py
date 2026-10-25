from app.services.app_marketplace_platform_cosmic_anvil import get_cosmic_anvil
def test_cosmic_anvil():
    r = get_cosmic_anvil()
    assert r["cosmic_strikes"] > 4000
    assert len(r["laws_created"]) == 3
    assert r["sparks"].startswith("GREEN")
    assert "tested" in r["laws_created"]["first_law"]
    assert "NEVER STOPS" in r["status"]
