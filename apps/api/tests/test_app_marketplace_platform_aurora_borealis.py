from app.services.app_marketplace_platform_aurora_borealis import get_aurora_borealis
def test_aurora_borealis():
    r = get_aurora_borealis()
    assert r["displays"] > 4000
    assert len(r["colors"]) == 4
    assert "passing" in r["colors"]["green"]
    assert r["latitude"].startswith("EVERYWHERE")
    assert "NEVER STOPS" in r["status"]
