from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_dedup import fleet_ai_data_dedup
def test_dd():
    r = fleet_ai_data_dedup([{"active": True, "processed_24h": 100000000, "removed": 15000000, "reduction_pct": 15}])
    assert r["removed"] == 15000000
    assert r["clean"]
