from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_sdk_v9 import fleet_api_sdk_v9
def test_asdk_v9():
    r = fleet_api_sdk_v9([{"generated": True, "published": True, "language": "python", "downloads_total": 50000}])
    assert r["languages"] == 1
    assert r["healthy"]
