from app.services.app_marketplace_app_app_app_app_app_app_app_chaos_eng import (
    create_experiment, simulate_impact, experiment_report,
)

def test_create():
    r = create_experiment("latency test", "api", "latency", 120, 2.0)
    assert r["created"]
    assert r["id"].startswith("chaos_")
    r2 = create_experiment("bad", "x", "invalid")
    assert not r2["created"]

def test_simulate():
    exp = create_experiment("lat", "api", "latency", magnitude=1.5)
    impact = simulate_impact(exp, {"p99_ms": 100, "error_rate": 0.5})
    assert impact["impact"]["p99_ms"] > 100
    assert impact["impact"]["degraded"]

def test_report():
    exp = create_experiment("err", "api", "error")
    impact = simulate_impact(exp, {"error_rate": 0.1})
    r = experiment_report(exp, impact)
    assert "recommendation" in r
