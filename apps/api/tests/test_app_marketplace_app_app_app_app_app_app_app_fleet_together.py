from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_together import fleet_together_status
def test_tg():
    r = fleet_together_status([{"deployed": True, "inferences_24h": 1000000, "gpu_hours_24h": 500}])
    assert r["inferences_24h"] == 1000000
    assert r["all_deployed"]
