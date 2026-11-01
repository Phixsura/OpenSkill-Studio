from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v107_18k import platform_v107_18k
def test_v107():
    r = platform_v107_18k()
    assert r["version"] == "107.0"
    assert "18,000" in r["milestone"]
