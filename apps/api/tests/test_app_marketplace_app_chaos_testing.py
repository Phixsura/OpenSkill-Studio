from app.services.app_marketplace_app_chaos_testing import create_experiment, evaluate_resilience

def test_create():
    r = create_experiment(app_id="a1", fault_type="latency", config={"delay_ms": 500}, duration_sec=60)
    assert r["experiment_id"].startswith("chaos_")
    assert r["safety_stop"]

def test_invalid_type():
    r = create_experiment(app_id="a1", fault_type="nuke", config={})
    assert "error" in r

def test_resilient():
    r = evaluate_resilience(
        before={"error_rate": 0.1, "p95_ms": 100},
        during={"error_rate": 2.0, "p95_ms": 300},
        after={"error_rate": 0.1, "p95_ms": 100, "recovery_time_sec": 15})
    assert r["grade"] == "A"
    assert r["fully_recovered"]

def test_fragile():
    r = evaluate_resilience(
        before={"error_rate": 0.1, "p95_ms": 100},
        during={"error_rate": 50, "p95_ms": 2000},
        after={"error_rate": 5.0, "p95_ms": 300, "recovery_time_sec": 120})
    assert r["grade"] == "F"
    assert not r["fully_recovered"]
