from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v90 import platform_v90
def test_v90():
    assert platform_v90()["version"] == "90.0"
    assert platform_v90()["lines"] >= 331000
