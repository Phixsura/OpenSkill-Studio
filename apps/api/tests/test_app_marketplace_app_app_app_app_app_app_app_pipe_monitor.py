from app.services.app_marketplace_app_app_app_app_app_app_app_pipe_monitor import monitor_pipeline, stale_pipelines

def test_monitor():
    r = monitor_pipeline([
        {"status": "success", "rows_processed": 10000, "duration_ms": 5000},
        {"status": "success", "rows_processed": 8000, "duration_ms": 4000},
        {"status": "failed", "rows_processed": 0, "duration_ms": 1000},
    ])
    assert r["success_rate"] == 66.7
    assert r["total_rows"] == 18000
    assert not r["healthy"]

def test_stale():
    r = stale_pipelines([
        {"name": "etl-users", "hours_since_last_run": 30},
        {"name": "etl-orders", "hours_since_last_run": 12},
    ], max_age_hours=24)
    assert len(r) == 1
    assert r[0]["name"] == "etl-users"
