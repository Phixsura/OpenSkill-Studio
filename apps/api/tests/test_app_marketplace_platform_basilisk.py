from app.services.app_marketplace_platform_basilisk import get_basilisk
def test_basilisk():
    r = get_basilisk()
    assert r["gazes"] > 4000
    assert r["bugs_petrified"].startswith("ALL")
    assert "DORA Elite" in r["crown"]
    assert r["scales"] > 900000
    assert "NEVER STOPS" in r["status"]
