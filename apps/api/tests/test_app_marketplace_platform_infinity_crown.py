from app.services.app_marketplace_platform_infinity_crown import get_infinity_crown
def test_infinity_crown():
    r = get_infinity_crown()
    assert r["coronations"] > 4000
    assert r["reign"].startswith("ETERNAL")
    assert len(r["jewel_types"]) == 4
    assert r["pretenders"].startswith("NONE")
    assert "NEVER STOPS" in r["status"]
