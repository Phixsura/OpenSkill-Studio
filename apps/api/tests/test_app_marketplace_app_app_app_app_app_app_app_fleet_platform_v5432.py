from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v5432 import platform_v5432
def test_v5432():
    assert platform_v5432()["version"] == "5432.0"
