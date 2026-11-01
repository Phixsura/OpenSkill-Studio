from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v99 import platform_v99
def test_v99():
    assert platform_v99()["version"] == "99.0"
    assert "v100" in platform_v99()["status"]
