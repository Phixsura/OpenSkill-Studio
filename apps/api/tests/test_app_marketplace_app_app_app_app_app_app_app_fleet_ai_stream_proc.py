from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_stream_proc import fleet_ai_stream_processor
def test_sp():
    r = fleet_ai_stream_processor([{"active": True, "eps": 1000000, "partitions": 256, "lag": 100}])
    assert r["eps"] == 1000000
    assert r["caught_up"]
