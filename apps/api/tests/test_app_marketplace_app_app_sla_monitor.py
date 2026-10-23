from app.services.app_marketplace_app_app_sla_monitor import check_sla, build_sla_report

def test_uptime_pass():
    r = check_sla(metric="uptime", target=99.9, actual=99.95)
    assert r["met"]
    assert r["margin"] == 0.05

def test_latency_pass():
    r = check_sla(metric="p99_latency_ms", target=200, actual=150, lower_is_better=True)
    assert r["met"]

def test_latency_fail():
    r = check_sla(metric="p99_latency_ms", target=200, actual=250, lower_is_better=True)
    assert not r["met"]

def test_report():
    checks = [
        {"metric": "uptime", "target": 99.9, "actual": 99.95},
        {"metric": "latency", "target": 200, "actual": 250, "lower_is_better": True},
    ]
    r = build_sla_report(checks=checks)
    assert r["passed"] == 1
    assert r["failed"] == 1
    assert r["overall"] == "non-compliant"
