from app.services.app_marketplace_error_reporting import (
    ErrorReportingService, ErrorReport, ErrorSeverity, ErrorState,
)


def test_report_and_group():
    ers = ErrorReportingService()
    r1 = ErrorReport("r1", "ext-1", "TypeError", "Cannot read property 'x'", org_id="org-1")
    r2 = ErrorReport("r2", "ext-1", "TypeError", "Cannot read property 'x'", org_id="org-2")
    g1 = ers.report(r1)
    g2 = ers.report(r2)
    assert g1.fingerprint == g2.fingerprint  # same group
    assert g2.count == 2
    assert len(g2.affected_orgs) == 2


def test_different_errors_different_groups():
    ers = ErrorReportingService()
    ers.report(ErrorReport("r1", "ext-2", "TypeError", "error A"))
    ers.report(ErrorReport("r2", "ext-2", "ValueError", "error B"))
    groups = ers.get_groups("ext-2")
    assert len(groups) == 2


def test_severity_escalation():
    ers = ErrorReportingService()
    for i in range(15):
        ers.report(ErrorReport(f"r{i}", "ext-3", "Error", "repeated",
                                severity=ErrorSeverity.LOW))
    groups = ers.get_groups("ext-3")
    assert groups[0].severity == ErrorSeverity.MEDIUM


def test_update_state():
    ers = ErrorReportingService()
    ers.report(ErrorReport("r1", "ext-4", "Bug", "oops"))
    groups = ers.get_groups("ext-4")
    fp = groups[0].fingerprint
    ers.update_state(fp, ErrorState.RESOLVED)
    resolved = ers.get_groups("ext-4", state=ErrorState.RESOLVED)
    assert len(resolved) == 1


def test_summary():
    ers = ErrorReportingService()
    for i in range(5):
        ers.report(ErrorReport(f"r{i}", "ext-5", "Err", "msg", org_id=f"org-{i}"))
    summary = ers.get_summary("ext-5")
    assert summary["total_reports"] == 5
    assert summary["unique_orgs_affected"] == 5
    assert summary["open"] == 1
