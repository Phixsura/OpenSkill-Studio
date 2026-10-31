from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_samp import fleet_ai_data_sampler
def test_ds():
    r = fleet_ai_data_sampler([{"active": True, "sampled_24h": 10000000, "strategies": ["random", "stratified", "cluster"], "repr_score": 95}])
    assert r["strategies"] == 3
    assert r["balanced"]
