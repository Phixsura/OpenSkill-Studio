from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v148 import platform_v148
def test_v148():
    assert platform_v148()["version"] == "148.0"
    assert "v150" in platform_v148()["status"]
