from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_res_rec import fleet_resource_recommendations
def test_rec():
    r = fleet_resource_recommendations([{"cpu_usage_pct": 10, "cpu_request_mcpu": 500}, {"cpu_usage_pct": 95, "cpu_request_mcpu": 200}, {"cpu_usage_pct": 50, "cpu_request_mcpu": 300}])
    assert r["over_provisioned"] == 1
    assert r["under_provisioned"] == 1
    assert r["savings_possible"]
