from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_batch_job import fleet_batch_job_metrics
def test_batch():
    r = fleet_batch_job_metrics([{"status": "completed", "duration_min": 30}, {"status": "failed"}])
    assert r["completed"] == 1
    assert r["failed"] == 1
    assert not r["reliable"]
