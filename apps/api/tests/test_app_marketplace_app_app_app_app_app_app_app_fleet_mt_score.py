from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mt_score import fleet_mt_score
def test_mt():
    r = fleet_mt_score({"data_isolation": 95, "compute_isolation": 90, "network_isolation": 85})
    assert r["score"] == 90.0
    assert r["enterprise_ready"]
