from app.services.app_marketplace_extension_dashboard_summary import (
    ExtensionDashboardSummaryService, TrendMetric,
)


def test_trend_up():
    tm = TrendMetric(150, 100, "installs")
    assert tm.change_percent == 50.0
    assert tm.trend == "up"


def test_trend_down():
    tm = TrendMetric(80, 100, "installs")
    assert tm.change_percent == -20.0
    assert tm.trend == "down"


def test_generate_summary():
    svc = ExtensionDashboardSummaryService()
    result = svc.generate({
        "installs": 1500, "installs_prev": 1000,
        "revenue_cents": 50000, "revenue_cents_prev": 40000,
        "api_calls": 100000, "api_calls_prev": 80000,
        "health_score": 95, "error_rate": 2.5, "avg_rating": 4.5,
        "extensions_count": 10,
    })
    assert len(result["trends"]) == 3
    assert result["health_score"] == 95
    assert result["total_installs"] == 1500


def test_alerts_high_error():
    svc = ExtensionDashboardSummaryService()
    result = svc.generate({"error_rate": 15})
    assert any(a["severity"] == "critical" for a in result["alerts"])


def test_alerts_low_rating():
    svc = ExtensionDashboardSummaryService()
    result = svc.generate({"avg_rating": 2.5})
    assert any("rating" in a["message"].lower() for a in result["alerts"])


def test_no_alerts_healthy():
    svc = ExtensionDashboardSummaryService()
    result = svc.generate({"error_rate": 1, "health_score": 99, "avg_rating": 4.8})
    assert len(result["alerts"]) == 0
