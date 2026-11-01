from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_resp_stream import fleet_ai_response_streamer
def test_rs():
    r = fleet_ai_response_streamer([{"active": True, "streams_24h": 10000000, "tokens": 100000000000, "ttft_ms": 80}])
    assert r["streams_24h"] == 10000000
    assert r["responsive"]
