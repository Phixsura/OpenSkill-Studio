from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_compression_v9 import fleet_api_compression_v9
def test_acomp_v9():
    r = fleet_api_compression_v9([{"compression_enabled": True, "bytes_saved_mb": 500, "compression_ratio": 0.7}])
    assert r["compressed"] == 1
    assert r["healthy"]
