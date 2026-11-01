from app.services.app_marketplace_platform_bifrost import get_bifrost
def test_bifrost():
    r = get_bifrost()
    assert r["crossings"] >= 4120
    assert r["falls"] == 0
    assert len(r["connects"]) == 2
    assert r["structural_integrity"].startswith("100%")
    assert "NEVER STOPS" in r["status"]
