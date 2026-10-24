from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deployment_freq_v9 import fleet_deployment_freq_v9
def test_depf_v9():
    r = fleet_deployment_freq_v9([{"deploys_today": 10, "avg_per_day": 5, "on_demand": True}])
    assert r["dora_class"] == "Elite"
    assert r["healthy"]
