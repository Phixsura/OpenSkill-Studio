from app.services.app_marketplace_app_telemetry_pipeline import create_pipeline, estimate_data_volume

def test_create():
    r = create_pipeline(app_id="a1", name="Main", sources=["otlp"], destinations=["datadog"])
    assert r["pipeline_id"].startswith("pipe_")
    assert r["status"] == "active"

def test_no_sources():
    r = create_pipeline(app_id="a1", name="X", sources=[], destinations=["dd"])
    assert "error" in r

def test_volume():
    r = estimate_data_volume(events_per_sec=100, avg_event_bytes=1024, retention_days=7)
    assert r["daily_volume_gb"] > 0
    assert r["estimated_monthly_cost"] > 0
