from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sev_dist import fleet_severity_dist
def test_sev():
    r = fleet_severity_dist([{"severity": 1}, {"severity": 2}, {"severity": 2}, {"severity": 3}])
    assert r["sev1_count"] == 1
    assert r["critical"]
