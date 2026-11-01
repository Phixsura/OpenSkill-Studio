from app.services.app_marketplace_platform_tidal_force import get_tidal_force
def test_tidal_force():
    r = get_tidal_force()
    assert "TSUNAMI" in r["amplitude"]
    assert r["ocean_displaced"]["failures"] == 0
    assert r["warning_level"].startswith("NONE")
    assert "NEVER STOPS" in r["status"]
