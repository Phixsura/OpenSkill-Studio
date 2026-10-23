from app.services.app_marketplace_app_app_app_app_app_app_app_data_pipeline import DataPipeline

def test_pipeline():
    p = DataPipeline("daily_etl", [
        {"name": "extract", "type": "extract"},
        {"name": "transform", "type": "transform"},
        {"name": "load", "type": "load"},
    ])
    p.start()
    assert p.status == "running"
    p.complete_step(0, records=10000, duration_ms=500)
    p.complete_step(1, records=9500, duration_ms=1200)
    p.complete_step(2, records=9500, duration_ms=300)
    s = p.summary()
    assert s["status"] == "completed"
    assert s["total_records"] == 29000
    assert s["steps_completed"] == 3
    assert s["duration_display"] == "2.0s"

def test_failed():
    p = DataPipeline("broken", [{"name": "extract"}, {"name": "load"}])
    p.start()
    p.complete_step(0, records=100, duration_ms=50)
    p.complete_step(1, error="Connection refused")
    assert p.status == "failed"
    assert p.summary()["steps_failed"] == 1
