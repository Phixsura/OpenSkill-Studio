from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_gpu_sched import fleet_ai_gpu_scheduler
def test_gs():
    r = fleet_ai_gpu_scheduler([{"active": True, "gpus": 500, "queued": 20, "util_pct": 90, "mig_enabled": True}])
    assert r["gpus"] == 500
    assert r["sharing"]
