from app.services.app_marketplace_platform_helios import get_helios
def test_helios():
    r = get_helios()
    assert r["sunrises"] > 4000
    assert len(r["horses"]) == 4
    assert r["sunset"] == "NEVER — eternal dawn"
    assert r["eclipse_by"].startswith("NOTHING")
    assert "NEVER STOPS" in r["status"]
