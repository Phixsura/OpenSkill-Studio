from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_job_queue import fleet_ai_job_queue
def test_jq():
    r = fleet_ai_job_queue([{"active": True, "pending": 100, "processing": 50, "completed_24h": 100000, "workers": 200}])
    assert r["workers"] == 200
    assert r["busy"]
