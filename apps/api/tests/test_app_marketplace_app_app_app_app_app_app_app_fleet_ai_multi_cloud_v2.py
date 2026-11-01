from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_multi_cloud_v2 import fleet_ai_multi_cloud_v2
def test_mcv2():
    r = fleet_ai_multi_cloud_v2([{"active": True, "clouds": ["aws", "gcp", "azure"], "deployments": 500, "failover_ok": True}])
    assert len(r["clouds"]) == 3
    assert r["multi_cloud"]
