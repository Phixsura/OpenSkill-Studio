from app.services.app_marketplace_extension_sla_monitor import (
    SLAMonitor, SLATarget, SLAMetrics,
)


def test_compliant():
    mon = SLAMonitor()
    mon.set_target(SLATarget("ext-1", uptime_target=99.9, latency_p99_ms=500, error_rate_max=1.0))
    mon.update_metrics("ext-1", SLAMetrics(uptime_actual=99.95, latency_p99_actual=250, error_rate_actual=0.5))
    result = mon.check_compliance("ext-1")
    assert result["compliant"] is True
    assert result["sla_score"] == 100.0


def test_uptime_violation():
    mon = SLAMonitor()
    mon.set_target(SLATarget("ext-2", uptime_target=99.9))
    mon.update_metrics("ext-2", SLAMetrics(uptime_actual=99.5))
    result = mon.check_compliance("ext-2")
    assert result["compliant"] is False
    assert "uptime" in result["violations"]


def test_latency_violation():
    mon = SLAMonitor()
    mon.set_target(SLATarget("ext-3", latency_p99_ms=200))
    mon.update_metrics("ext-3", SLAMetrics(latency_p99_actual=350))
    result = mon.check_compliance("ext-3")
    assert result["checks"]["latency_p99"]["met"] is False


def test_multiple_violations():
    mon = SLAMonitor()
    mon.set_target(SLATarget("ext-4", uptime_target=99.9, error_rate_max=1.0))
    mon.update_metrics("ext-4", SLAMetrics(uptime_actual=95.0, error_rate_actual=5.0))
    result = mon.check_compliance("ext-4")
    assert len(result["violations"]) == 2
    assert result["sla_score"] < 100


def test_sla_report():
    mon = SLAMonitor()
    mon.set_target(SLATarget("ext-5"))
    mon.update_metrics("ext-5", SLAMetrics(uptime_actual=100.0))
    report = mon.get_sla_report("ext-5")
    assert "total_violations" in report


def test_compliance_summary():
    mon = SLAMonitor()
    mon.set_target(SLATarget("good"))
    mon.set_target(SLATarget("bad"))
    mon.update_metrics("good", SLAMetrics(uptime_actual=100.0))
    mon.update_metrics("bad", SLAMetrics(uptime_actual=90.0))
    summary = mon.get_compliance_summary()
    assert summary["total_extensions"] == 2
    assert summary["compliant"] == 1
    assert summary["compliance_rate"] == 50.0
