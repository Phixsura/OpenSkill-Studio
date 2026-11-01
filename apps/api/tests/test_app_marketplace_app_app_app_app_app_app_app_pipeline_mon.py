from app.services.app_marketplace_app_app_app_app_app_app_app_pipeline_mon import monitor_pipeline, pipeline_summary

def test_monitor():
    r = monitor_pipeline("etl-users", [
        {"name": "extract", "records_processed": 10000, "errors": 0, "duration_sec": 30},
        {"name": "transform", "records_processed": 10000, "errors": 5, "duration_sec": 120},
        {"name": "load", "records_processed": 9995, "errors": 0, "duration_sec": 45},
    ])
    assert r["total_records"] == 29995
    assert r["total_errors"] == 5
    assert r["bottleneck"] == "transform"
    assert not r["healthy"]

def test_summary():
    pipelines = [{"healthy": True, "total_records": 1000}, {"healthy": False, "total_records": 500}]
    r = pipeline_summary(pipelines)
    assert r["healthy"] == 1
    assert r["total_records"] == 1500
