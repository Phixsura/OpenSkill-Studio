from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_eval_data import fleet_ai_eval_dataset
def test_ed():
    r = fleet_ai_eval_dataset([{"active": True, "datasets": 100, "samples": 10000000, "domains": 25}])
    assert r["datasets"] == 100
    assert r["comprehensive"]
