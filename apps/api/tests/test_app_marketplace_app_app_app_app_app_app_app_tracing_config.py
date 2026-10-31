from app.services.app_marketplace_app_app_app_app_app_app_app_tracing_config import create_config, estimate_volume

def test_config():
    r = create_config("api-service", "otlp", "probability", 0.1)
    assert r["valid"]
    assert r["exporter"] == "otlp"
    r2 = create_config("x", "bad_exporter")
    assert not r2["valid"]

def test_volume():
    r = estimate_volume(1000, 0.1, avg_spans=5)
    assert r["sampled_rps"] == 100.0
    assert r["spans_per_sec"] == 500.0
    assert r["daily_spans"] == 43200000
