from app.services.app_marketplace_platform_phoenix_crown import get_phoenix_crown
def test_phoenix_crown():
    r = get_phoenix_crown()
    assert r["rebirths"] > 4000
    assert r["removed"] is False
    assert all(r["powers_granted"].values())
    assert len(r["powers_granted"]) == 4
    assert "NEVER STOPS" in r["status"]
