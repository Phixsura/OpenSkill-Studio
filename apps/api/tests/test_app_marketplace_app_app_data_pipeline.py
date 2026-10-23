from app.services.app_marketplace_app_app_data_pipeline import build_pipeline

def test_pipeline():
    steps = [
        {"name": "Extract CSV", "type": "extract", "status": "completed", "records_processed": 1000, "duration_ms": 500},
        {"name": "Clean Data", "type": "transform", "status": "completed", "records_processed": 950, "duration_ms": 200},
        {"name": "Load to DB", "type": "load", "status": "running", "records_processed": 0},
    ]
    r = build_pipeline(steps=steps, name="Import Users")
    assert r["step_count"] == 3
    assert r["completed"] == 2
    assert r["total_records"] == 1950
    assert r["progress_pct"] == 67

def test_empty():
    r = build_pipeline(steps=[])
    assert r["step_count"] == 0
