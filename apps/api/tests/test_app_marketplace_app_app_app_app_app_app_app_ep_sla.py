from app.services.app_marketplace_app_app_app_app_app_app_app_ep_sla import check_endpoint_sla, sla_report

def test_compliant():
    r = check_endpoint_sla("/api/users",
        {"availability_pct": 99.99, "p99_ms": 100, "error_rate_pct": 0.1},
        {"availability": 99.9, "max_p99_ms": 500, "max_error_pct": 1})
    assert r["compliant"]

def test_non_compliant():
    r = check_endpoint_sla("/api/orders",
        {"availability_pct": 99.5, "p99_ms": 800, "error_rate_pct": 5},
        {"availability": 99.9, "max_p99_ms": 500, "max_error_pct": 1})
    assert not r["compliant"]

def test_report():
    endpoints = [
        check_endpoint_sla("/a", {"availability_pct": 100, "p99_ms": 50, "error_rate_pct": 0}, {"availability": 99.9, "max_p99_ms": 500, "max_error_pct": 1}),
        check_endpoint_sla("/b", {"availability_pct": 98, "p99_ms": 600, "error_rate_pct": 3}, {"availability": 99.9, "max_p99_ms": 500, "max_error_pct": 1}),
    ]
    r = sla_report(endpoints)
    assert r["compliance_pct"] == 50.0
