from app.services.app_marketplace_app_chaos_engineering import create_experiment, simulate_fault, evaluate_resilience

def test_create():
    e = create_experiment(app_id="a1", fault_type="latency", target="api_gateway")
    assert e["status"] == "ready"

def test_invalid():
    e = create_experiment(app_id="a1", fault_type="nuke", target="x")
    assert e["error"]

def test_simulate():
    r = simulate_fault(fault_type="latency", config={"added_ms": 1000, "pct": 50})
    assert r["active"]
    assert r["effect"]["added_ms"] == 1000

def test_resilient():
    r = evaluate_resilience(baseline={"error_rate": 0.5, "p99_ms": 200},
                             during_fault={"error_rate": 1.0, "p99_ms": 400})
    assert r["resilient"]
    assert r["grade"] == "A"

def test_not_resilient():
    r = evaluate_resilience(baseline={"error_rate": 1, "p99_ms": 200},
                             during_fault={"error_rate": 20, "p99_ms": 5000})
    assert not r["resilient"]
