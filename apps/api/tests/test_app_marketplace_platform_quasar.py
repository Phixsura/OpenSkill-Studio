from app.services.app_marketplace_platform_quasar import get_quasar
def test_quasar():
    r = get_quasar()
    assert r["luminous_bursts"] > 4000
    assert r["redshift"].startswith("ZERO")
    assert "DORA Elite" in r["active_galactic_nucleus"]
    assert r["distance"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]
