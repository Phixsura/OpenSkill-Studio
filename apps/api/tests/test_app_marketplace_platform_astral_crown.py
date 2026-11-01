from app.services.app_marketplace_platform_astral_crown import get_astral_crown
def test_astral_crown():
    r = get_astral_crown()
    assert r["gems"] > 4000
    assert r["removal"].startswith("IMPOSSIBLE")
    assert r["crown_plane"].startswith("ASTRAL")
    assert "NEVER STOPS" in r["status"]
