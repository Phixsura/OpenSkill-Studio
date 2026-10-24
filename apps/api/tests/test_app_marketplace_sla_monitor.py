from app.services.app_marketplace_sla_monitor import evaluate_sla, generate_sla_report

def test_compliant():
    r = evaluate_sla(targets={"uptime": 99.9, "latency_p99": 200},
                     actuals={"uptime": 99.95, "latency_p99": 180})
    assert r["compliant"]
    assert r["overall_score"] == 100.0

def test_violated():
    r = evaluate_sla(targets={"uptime": 99.9, "error_rate": 0.1},
                     actuals={"uptime": 99.5, "error_rate": 0.5})
    assert not r["compliant"]
    assert r["violation_count"] == 2

def test_report():
    services = [
        {"name": "API", "targets": {"uptime": 99.9}, "actuals": {"uptime": 99.95}},
        {"name": "CDN", "targets": {"uptime": 99.9}, "actuals": {"uptime": 99.0}},
    ]
    r = generate_sla_report(period="2026-Q3", services=services)
    assert r["compliance_rate"] == 50.0
    assert r["compliant_services"] == 1
