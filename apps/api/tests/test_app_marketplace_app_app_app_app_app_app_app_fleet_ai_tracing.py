from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tracing import fleet_ai_tracing
def test_tr():
    r = fleet_ai_tracing([{"active": True, "traces_24h": 50000000, "spans_24h": 500000000, "avg_depth": 8}])
    assert r["traces_24h"] == 50000000
    assert r["deep"]
