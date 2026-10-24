from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v365 import platform_v365
def test_v365():
    assert platform_v365()["version"] == "365.0"
