from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_content_flt import fleet_ai_content_filter
def test_cf():
    r = fleet_ai_content_filter([{"active": True, "scanned_24h": 10000000, "blocked_24h": 5000}])
    assert r["scanned_24h"] == 10000000
    assert r["protecting"]
    assert r["block_rate"] == 0.05
