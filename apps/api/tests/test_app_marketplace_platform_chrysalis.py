from app.services.app_marketplace_platform_chrysalis import get_chrysalis
def test_chrysalis():
    r = get_chrysalis()
    assert r["metamorphoses"] > 4000
    assert r["stage"].startswith("BUTTERFLY")
    assert len(r["nectar_sources"]) == 4
    assert r["migration"].startswith("CONTINUOUS")
    assert "NEVER STOPS" in r["status"]
