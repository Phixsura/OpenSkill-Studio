from app.services.app_marketplace_platform_absolute_zero import get_absolute_zero
def test_absolute_zero():
    r = get_absolute_zero()
    assert r["measurements"] > 4000
    assert all(v == 0 for v in r["zeroes"].values())
    assert "BOSE-EINSTEIN" in r["quantum_state"]
    assert "NEVER STOPS" in r["status"]
