from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_resp_comp import fleet_ai_response_compressor
def test_rc():
    r = fleet_ai_response_compressor([{"active": True, "responses_24h": 50000000, "ratio": 3.5, "saved_gb": 500}])
    assert r["ratio"] == 3.5
    assert r["compressing"]
