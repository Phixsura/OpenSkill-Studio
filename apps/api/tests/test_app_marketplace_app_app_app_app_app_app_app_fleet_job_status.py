from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_job_status import fleet_job_status
def test_jobs():
    r = fleet_job_status([{"status": "succeeded"}, {"status": "succeeded"}, {"status": "failed"}, {"status": "running"}])
    assert r["succeeded"] == 2
    assert r["failed"] == 1
    assert r["success_rate"] == 50.0
