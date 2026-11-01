from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_pipe_v2 import fleet_ai_data_pipeline_v2
def test_dpv2():
    r = fleet_ai_data_pipeline_v2([{"active": True, "stages": 20, "records_24h": 500000000, "throughput_mbs": 5000}])
    assert r["records_24h"] == 500000000
    assert r["streaming"]
