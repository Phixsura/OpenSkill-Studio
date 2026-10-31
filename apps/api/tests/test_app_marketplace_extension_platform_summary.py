from app.services.app_marketplace_extension_platform_summary import PlatformSummaryService


def test_update_and_summary():
    svc = PlatformSummaryService()
    svc.update(total_services=620, backend_services=276, frontend_components=344,
               total_tests=3000, total_commits=4841, security_fixes=47)
    s = svc.get_summary()
    assert s["scale"]["services"] == 620
    assert s["scale"]["tests"] == 3000


def test_achievements():
    svc = PlatformSummaryService()
    svc.update(total_services=620, total_tests=3000, total_commits=4841,
               backend_services=276, frontend_components=344,
               security_fixes=47, test_pass_rate=100.0, dora_classification="elite")
    achievements = svc.get_achievements()
    assert "🏆 600+ Services Built" in achievements
    assert "✅ 3,000+ Tests GREEN" in achievements
    assert "🚀 DORA Elite Performance" in achievements
    assert len(achievements) == 8  # all achievements unlocked!


def test_production_ready():
    svc = PlatformSummaryService()
    svc.update(total_tests=3000, test_pass_rate=100, uptime_percent=99.99,
               error_rate=0.3, security_fixes=47)
    result = svc.is_production_ready()
    assert result["ready"] is True


def test_not_production_ready():
    svc = PlatformSummaryService()
    svc.update(total_tests=50, test_pass_rate=80, error_rate=10)
    result = svc.is_production_ready()
    assert result["ready"] is False


def test_quality_metrics():
    svc = PlatformSummaryService()
    svc.update(test_pass_rate=100, uptime_percent=99.99, error_rate=0.1, avg_response_ms=42)
    s = svc.get_summary()
    assert s["quality"]["test_pass_rate"] == 100
    assert s["quality"]["avg_response_ms"] == 42


def test_growth_metrics():
    svc = PlatformSummaryService()
    svc.update(total_developers=2000, total_extensions=500,
               total_installs=100000, monthly_revenue_cents=5000000)
    s = svc.get_summary()
    assert s["growth"]["developers"] == 2000
    assert s["growth"]["mrr_cents"] == 5000000
