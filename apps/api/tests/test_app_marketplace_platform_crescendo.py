from app.services.app_marketplace_platform_crescendo import get_crescendo
def test_crescendo():
    r = get_crescendo()
    assert r["movement"] == "FORTISSIMO"
    assert r["peak_reached"] == False
    assert r["reason"] == "There is no peak. Only crescendo."
    assert "NEVER STOPS" in r["status"]
