from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_par import fleet_ai_model_parallelism
def test_mp():
    r = fleet_ai_model_parallelism([{"active": True, "gpus": 256, "tp": 8, "pp": 4, "efficiency_pct": 88}])
    assert r["gpus"] == 256
    assert r["scalable"]
