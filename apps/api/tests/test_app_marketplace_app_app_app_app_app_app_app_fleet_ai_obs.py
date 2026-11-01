from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_obs import fleet_ai_observability
def test_aio():
    r = fleet_ai_observability([{"active": True, "traces_24h": 1000000, "spans_24h": 5000000}])
    assert r["traces_24h"] == 1000000
    assert r["comprehensive"]
