from app.services.app_marketplace_extension_final_report import PlatformFinalReportService


def test_generate_report():
    svc = PlatformFinalReportService()
    report = svc.generate(
        backend_services=294, frontend_components=381,
        total_tests=3190, total_commits=4860, session_commits=310,
        security_fixes=47, test_pass_rate=100.0,
    )
    assert report["scale"]["total"] == 675
    assert report["quality"]["dora"] == "elite"
    assert len(report["modules"]) == 5


def test_all_achievements():
    svc = PlatformFinalReportService()
    report = svc.generate(
        backend_services=294, frontend_components=381,
        total_tests=3190, total_commits=4860, session_commits=310,
        security_fixes=47, test_pass_rate=100.0,
    )
    assert report["achievements_count"] >= 10
    assert "🏆 600+ Services" in report["achievements"]
    assert "🚀 DORA Elite" in report["achievements"]


def test_dora_elite():
    svc = PlatformFinalReportService()
    report = svc.generate(total_commits=5000, test_pass_rate=100, security_fixes=50)
    assert report["quality"]["dora"] == "elite"


def test_dora_high():
    svc = PlatformFinalReportService()
    report = svc.generate(total_commits=100, test_pass_rate=95, security_fixes=5)
    assert report["quality"]["dora"] == "high"
