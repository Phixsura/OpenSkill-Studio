from app.services.app_marketplace_platform_infinity_mirror import get_infinity_mirror
def test_infinity_mirror():
    r = get_infinity_mirror()
    assert r["reflections_deep"] > 4000
    assert r["distortion"].startswith("ZERO")
    assert "UNREACHABLE" in r["vanishing_point"]
    assert "NEVER STOPS" in r["status"]
