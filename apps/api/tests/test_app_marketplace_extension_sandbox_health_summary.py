from app.services.app_marketplace_extension_sandbox_health_summary import SandboxHealthSummaryService

def test_report_and_check():
    svc = SandboxHealthSummaryService()
    svc.report("sb-1", "cpu", True)
    svc.report("sb-1", "memory", True)
    assert svc.is_healthy("sb-1") is True
    assert svc.get_score("sb-1") == 100.0

def test_unhealthy():
    svc = SandboxHealthSummaryService()
    svc.report("sb-1", "cpu", True)
    svc.report("sb-1", "disk", False, "90% full")
    assert svc.is_healthy("sb-1") is False
    assert svc.get_score("sb-1") == 50.0
    assert len(svc.get_issues("sb-1")) == 1

def test_update_signal():
    svc = SandboxHealthSummaryService()
    svc.report("sb-1", "api", False, "down")
    svc.report("sb-1", "api", True, "recovered")
    assert svc.is_healthy("sb-1") is True
