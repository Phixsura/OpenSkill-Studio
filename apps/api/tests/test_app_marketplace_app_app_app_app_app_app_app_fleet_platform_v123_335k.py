from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v123_335k import platform_v123_335k
def test_v123():
    r = platform_v123_335k()
    assert r["version"] == "123.0"
    assert "335,000" in r["milestone"]
