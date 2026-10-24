from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v221 import platform_v221
def test_v221():
    assert platform_v221()["version"] == "221.0"
    assert "340K" in platform_v221()["status"]
