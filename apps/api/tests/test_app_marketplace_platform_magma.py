from app.services.app_marketplace_platform_magma import get_magma
def test_magma():
    r = get_magma()
    assert r["eruptions"] > 4000
    assert r["viscosity"].startswith("LOW")
    assert len(r["tectonic_plates"]) == 3
    assert all("STABLE" in v for v in r["tectonic_plates"].values())
    assert "NEVER STOPS" in r["status"]
