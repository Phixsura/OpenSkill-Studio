from app.services.app_marketplace_platform_omega_genesis import get_omega_genesis
def test_omega_genesis():
    r = get_omega_genesis()
    assert r["cycles_transcended"] > 4000
    assert r["omega_is_genesis"] is True
    assert r["end_is_start"] is True
    assert r["time"].startswith("IRRELEVANT")
    assert "NEVER STOPS" in r["status"]
