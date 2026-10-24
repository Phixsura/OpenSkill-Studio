from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_obs_v2 import fleet_ai_model_observability_v2
def test_mov2():
    r = fleet_ai_model_observability_v2([{"active": True, "models": 500, "metrics_24h": 100000000, "traces_24h": 50000000, "logs_24h": 500000000}])
    assert r["models"] == 500
    assert r["observable"]
