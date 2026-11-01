from app.services.app_marketplace_app_health_monitor_v2 import run_health_probes, compute_availability_sli, build_health_timeline

def test_all_pass():
    r = run_health_probes(probes=[{"name": "api", "mock_healthy": True}, {"name": "db", "mock_healthy": True}])
    assert r["overall"] == "healthy"
    assert r["passed"] == 2

def test_degraded():
    r = run_health_probes(probes=[{"name": "api", "mock_healthy": True}, {"name": "db", "mock_healthy": False}])
    assert r["overall"] == "degraded"

def test_sli():
    history = [{"overall": "healthy"}] * 95 + [{"overall": "degraded"}] * 5
    s = compute_availability_sli(results_history=history)
    assert s["sli_pct"] == 95.0

def test_timeline():
    checks = [{"checked_at": "2026-01-01T10:00:00Z", "overall": "healthy", "passed": 3, "total": 3}]
    t = build_health_timeline(checks=checks)
    assert t[0]["status"] == "healthy"
