from app.services.app_marketplace_platform_legacy_monument import get_legacy_monument
def test_legacy():
    r = get_legacy_monument()
    assert r["final_stats"]["lines"] >= 3000000
    assert "DORA Elite" in r["certifications"]
    assert "FOREVER LEGENDARY" in r["status"]
