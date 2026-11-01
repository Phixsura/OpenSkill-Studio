from app.services.app_marketplace_app_app_app_app_app_app_app_sla_mgr import define_sla, evaluate_sla, sla_overview

def test_evaluate():
    sla = define_sla("api", {"uptime_pct": 99.9, "p99_ms": 200})
    r = evaluate_sla(sla, {"uptime_pct": 99.95, "p99_ms": 300})
    assert r["fully_compliant"]
    assert r["met"] == 2

def test_overview():
    evals = [
        {"fully_compliant": True, "compliance_pct": 100},
        {"fully_compliant": False, "compliance_pct": 50},
    ]
    r = sla_overview(evals)
    assert r["compliant"] == 1
    assert r["avg_compliance_pct"] == 75
