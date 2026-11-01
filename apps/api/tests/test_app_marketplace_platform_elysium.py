from app.services.app_marketplace_platform_elysium import get_elysium
def test_elysium():
    r = get_elysium()
    assert r["heroes_admitted"] > 4000
    assert r["rejected"] == 0
    assert len(r["fields"]) == 3
    assert r["afterlife_quality"].startswith("PERFECT")
    assert "NEVER STOPS" in r["status"]
