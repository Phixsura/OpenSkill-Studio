from app.services.app_marketplace_platform_anvil import get_anvil
def test_anvil():
    r = get_anvil()
    assert r["hammer_falls"] > 4000
    assert r["pieces_forged"] > 900000
    assert r["surface"].startswith("PRISTINE")
    assert len(r["workpieces"]) == 3
    assert "NEVER STOPS" in r["status"]
