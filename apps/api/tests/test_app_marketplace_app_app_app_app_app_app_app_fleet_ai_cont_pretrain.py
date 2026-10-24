from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cont_pretrain import fleet_ai_continuous_pretraining
def test_cp():
    r = fleet_ai_continuous_pretraining([{"active": True, "tokens_total": 15000000000000, "loss": 1.45, "gpus": 2048}])
    assert r["gpus"] == 2048
    assert r["converging"]
