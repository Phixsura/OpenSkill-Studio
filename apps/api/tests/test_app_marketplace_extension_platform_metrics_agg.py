from app.services.app_marketplace_extension_platform_metrics_agg import PlatformMetricsAggService


def test_update_and_report():
    svc = PlatformMetricsAggService()
    svc.update(
        total_services=583, backend_services=263, frontend_components=320,
        total_tests=2870, total_commits=4831, test_pass_rate=100.0,
        avg_latency_ms=45, error_rate=0.3, uptime_percent=99.99,
        developer_count=2000, extension_count=500, install_count=100000,
    )
    report = svc.get_report()
    assert report["platform"]["services"] == 583
    assert report["platform"]["tests"] == 2870
    assert report["quality"]["test_pass_rate"] == 100.0


def test_dora_elite():
    svc = PlatformMetricsAggService()
    svc.update(total_commits=5000, test_pass_rate=100, error_rate=0.3, uptime_percent=99.99)
    report = svc.get_report()
    assert report["dora"]["classification"] == "elite"


def test_dora_high():
    svc = PlatformMetricsAggService()
    svc.update(total_commits=100, test_pass_rate=95, error_rate=2, uptime_percent=99.5)
    report = svc.get_report()
    assert report["dora"]["classification"] == "high"


def test_growth_metrics():
    svc = PlatformMetricsAggService()
    svc.update(developer_count=2000, extension_count=500, install_count=100000)
    report = svc.get_report()
    assert report["growth"]["developers"] == 2000
    assert report["growth"]["installs"] == 100000
