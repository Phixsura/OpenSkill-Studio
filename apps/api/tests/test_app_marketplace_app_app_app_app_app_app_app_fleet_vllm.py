from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_vllm import fleet_vllm_status
def test_vllm():
    r = fleet_vllm_status([{"running": True, "tokens_per_sec": 5000, "gpus": 8}])
    assert r["tokens_per_sec"] == 5000
    assert r["all_running"]
