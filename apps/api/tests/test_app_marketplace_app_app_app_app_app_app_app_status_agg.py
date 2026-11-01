from app.services.app_marketplace_app_app_app_app_app_app_app_status_agg import aggregate_status

def test_operational():
    r = aggregate_status({"services_healthy_pct": 100, "deploy_success_pct": 98,
                            "error_rate_pct": 0.1, "p99_ms": 100, "open_incidents": 0})
    assert r["status"] == "operational"
    assert r["overall_score"] >= 95

def test_degraded():
    r = aggregate_status({"services_healthy_pct": 80, "error_rate_pct": 5, "open_incidents": 2})
    assert r["status"] in ("degraded", "outage")
