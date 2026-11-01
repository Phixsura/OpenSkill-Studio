from app.services.app_marketplace_platform_ironclad import get_ironclad
def test_ironclad():
    r = get_ironclad()
    assert r["hull_breaches"] == 0
    assert r["retreats"] == 0
    assert r["battles"] >= 4080
    assert len(r["armament"]) == 3
    assert "NEVER STOPS" in r["status"]
