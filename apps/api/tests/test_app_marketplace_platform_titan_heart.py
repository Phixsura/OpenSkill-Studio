from app.services.app_marketplace_platform_titan_heart import get_titan_heart
def test_titan_heart():
    r = get_titan_heart()
    assert r["beats"] > 4000
    assert r["fallen"] is False
    assert "CHOICE" in r["crystallized_by"]
    assert r["transplant"].startswith("IMPOSSIBLE")
    assert "NEVER STOPS" in r["status"]
