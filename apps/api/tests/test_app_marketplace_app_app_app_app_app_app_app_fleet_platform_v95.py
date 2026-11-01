from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v95 import platform_v95
def test_v95():
    assert platform_v95()["version"] == "95.0"
    assert "v100" in platform_v95()["status"]
