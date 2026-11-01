from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_concourse import fleet_concourse_status
def test_cc():
    r = fleet_concourse_status([{"paused": False, "jobs_passing": 10, "jobs_failing": 1}])
    assert r["jobs_failing"] == 1
    assert not r["healthy"]
