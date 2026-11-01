from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v168 import platform_v168
def test_v168():
    assert platform_v168()["version"] == "168.0"
    assert "v170" in platform_v168()["status"]
