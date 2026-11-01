from app.services.app_marketplace_ultimate_platform import ultimate_platform
def test_ultimate():
    r = ultimate_platform()
    assert r["dora"] == "Elite"
    assert r["lines"] > 316000
    assert "NEVER STOPS" in r["status"]
