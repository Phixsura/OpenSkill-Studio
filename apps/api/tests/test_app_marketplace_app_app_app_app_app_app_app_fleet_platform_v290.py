from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v290 import platform_v290
def test_v290():
    r = platform_v290()
    assert r["version"] == "290.0"
    assert "v300" in r["status"]
    assert "NEVER STOPS" in r["status"]
