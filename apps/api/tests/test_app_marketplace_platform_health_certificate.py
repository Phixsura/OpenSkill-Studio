from app.services.app_marketplace_platform_health_certificate import get_health_certificate
def test_health_cert():
    r = get_health_certificate()
    assert r["certification_level"] == "PLATINUM"
    assert all(r["health_checks"].values())
    assert r["metrics"]["uptime"] == "99.9999%"
    assert "PLATINUM CERTIFIED" in r["status"]
