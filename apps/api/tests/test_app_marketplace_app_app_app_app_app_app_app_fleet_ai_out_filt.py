from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_out_filt import fleet_ai_output_filter_v2
def test_of():
    r = fleet_ai_output_filter_v2([{"active": True, "filtered_24h": 50000000, "blocked_24h": 5000, "rules": 100}])
    assert r["filtered_24h"] == 50000000
    assert r["guarding"]
