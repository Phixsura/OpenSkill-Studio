from app.services.app_marketplace_extension_sla_monitor import SlaMonitorService


def test_perfect_slo():
    svc = SlaMonitorService()
    svc.define_slo("availability", 0.999, window_seconds=3600)
    svc.record_batch("availability", good_count=1000, total_count=1000)
    status = svc.get_status("availability")
    assert status.current == 1.0
    assert status.error_budget_pct == 100
    assert status.alerting is False


def test_degraded_slo():
    svc = SlaMonitorService()
    svc.define_slo("availability", 0.999, window_seconds=3600)
    svc.record_batch("availability", good_count=990, total_count=1000)
    status = svc.get_status("availability")
    assert status.current == 0.99
    # 99.9% target allows 1 error per 1000, but we have 10
    assert status.error_budget_remaining < status.error_budget_total


def test_budget_exhausted():
    svc = SlaMonitorService()
    svc.define_slo("latency", 0.99, window_seconds=3600)
    svc.record_batch("latency", good_count=900, total_count=1000)
    # 99% target allows 10 errors, we have 100
    status = svc.get_status("latency")
    assert status.error_budget_remaining == 0
    assert status.error_budget_pct == 0


def test_burn_rate():
    svc = SlaMonitorService()
    svc.define_slo("slo", 0.999, window_seconds=3600)
    # 0.1% budget, but we're producing 1% errors = 10x burn rate
    svc.record_batch("slo", good_count=990, total_count=1000)
    status = svc.get_status("slo")
    assert status.burn_rate == 10.0


def test_burn_rate_alert():
    svc = SlaMonitorService()
    svc.define_slo("slo", 0.999, window_seconds=3600, burn_rate_threshold=5.0)
    svc.record_batch("slo", good_count=990, total_count=1000)
    status = svc.get_status("slo")
    assert status.alerting is True  # 10x > 5x threshold


def test_no_alert_normal():
    svc = SlaMonitorService()
    svc.define_slo("slo", 0.999, window_seconds=3600, burn_rate_threshold=5.0)
    svc.record_batch("slo", good_count=999, total_count=1000)
    status = svc.get_status("slo")
    assert status.alerting is False


def test_individual_records():
    svc = SlaMonitorService()
    svc.define_slo("api", 0.99, window_seconds=3600)
    for _ in range(95):
        svc.record("api", True)
    for _ in range(5):
        svc.record("api", False)
    status = svc.get_status("api")
    assert status.current == 0.95


def test_no_events():
    svc = SlaMonitorService()
    svc.define_slo("empty", 0.999)
    status = svc.get_status("empty")
    assert status.current == 1.0
    assert status.alerting is False


def test_all_statuses():
    svc = SlaMonitorService()
    svc.define_slo("a", 0.999)
    svc.define_slo("b", 0.99)
    svc.record_batch("a", 999, 1000)
    svc.record_batch("b", 95, 100)
    statuses = svc.get_all_statuses()
    assert len(statuses) == 2
