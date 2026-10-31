from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tracing_v4 import fleet_ai_tracing_v4
def test_tv4():
    r = fleet_ai_tracing_v4([{"active": True, "traces_24h": 1000000000, "spans_24h": 10000000000, "sampling_pct": 10}])
    assert r["traces_24h"] == 1000000000
    assert r["tracing"]
