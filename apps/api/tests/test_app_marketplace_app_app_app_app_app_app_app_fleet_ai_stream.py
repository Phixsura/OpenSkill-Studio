from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_stream import fleet_ai_streaming
def test_ais():
    r = fleet_ai_streaming([{"active": True, "active_streams": 1000, "tokens_streamed_24h": 500000000}])
    assert r["active_streams"] == 1000
    assert r["all_active"]
