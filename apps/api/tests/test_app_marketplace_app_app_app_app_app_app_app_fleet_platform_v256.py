from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v256 import platform_v256
def test_v256():
    assert platform_v256()["version"] == "256.0"
    assert platform_v256()["note"] == "v256 = 2^8!"
