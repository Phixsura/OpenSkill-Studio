from app.services.app_marketplace_extension_health_dashboard import (
    HealthDashboardService, HealthState,
)


def test_report_and_summary():
    svc = HealthDashboardService()
    svc.report("API Gateway", "infrastructure", HealthState.HEALTHY)
    svc.report("Search Index", "infrastructure", HealthState.HEALTHY)
    summary = svc.get_summary()
    assert summary["total_services"] == 2
    assert summary["overall_score"] == 100.0
    assert summary["overall_state"] == "healthy"


def test_degraded_score():
    svc = HealthDashboardService()
    svc.report("API", "infra", HealthState.HEALTHY)
    svc.report("DB", "infra", HealthState.DEGRADED)
    score = svc.get_overall_score()
    assert score == 80.0  # (100 + 60) / 2


def test_issues_sorted():
    svc = HealthDashboardService()
    svc.report("A", "ext", HealthState.DEGRADED, "slow")
    svc.report("B", "ext", HealthState.DOWN, "crashed")
    svc.report("C", "ext", HealthState.CRITICAL, "errors")
    issues = svc.get_issues()
    assert issues[0].severity == "critical"
    assert issues[1].severity == "high"
    assert issues[2].severity == "medium"


def test_by_category():
    svc = HealthDashboardService()
    svc.report("ext-1", "extension", HealthState.HEALTHY)
    svc.report("conn-1", "connector", HealthState.HEALTHY)
    svc.report("ext-2", "extension", HealthState.DEGRADED)
    by_cat = svc.get_by_category()
    assert len(by_cat["extension"]) == 2
    assert len(by_cat["connector"]) == 1


def test_overall_state_thresholds():
    svc = HealthDashboardService()
    svc.report("A", "x", HealthState.DOWN)
    assert svc.get_overall_state() == HealthState.DOWN
    svc.report("B", "x", HealthState.HEALTHY)
    svc.report("C", "x", HealthState.HEALTHY)
    # (0 + 100 + 100) / 3 = 66.7 → degraded
    assert svc.get_overall_state() == HealthState.DEGRADED


def test_no_issues_when_healthy():
    svc = HealthDashboardService()
    svc.report("A", "x", HealthState.HEALTHY)
    assert len(svc.get_issues()) == 0


def test_empty_dashboard():
    svc = HealthDashboardService()
    assert svc.get_overall_score() == 100.0
    assert svc.get_summary()["total_services"] == 0
