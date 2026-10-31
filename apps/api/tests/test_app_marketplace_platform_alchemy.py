from app.services.app_marketplace_platform_alchemy import get_alchemy
def test_alchemy():
    r = get_alchemy()
    assert r["transmutations"] > 4000
    assert "Testing" in r["philosophers_stone"]
    assert len(r["elements"]) == 4
    assert "DORA Elite" in r["magnum_opus"]
    assert "NEVER STOPS" in r["status"]
