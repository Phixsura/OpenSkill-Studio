from app.services.app_marketplace_extension_canary_analysis import (
    CanaryAnalysisService, MetricSample
)


def test_error_rate_pass():
    svc = CanaryAnalysisService()
    j = svc.compare_error_rates(
        baseline_errors=10, baseline_total=10000,
        canary_errors=12, canary_total=10000)
    assert j.verdict in ("pass", "inconclusive")  # small diff, likely not significant


def test_error_rate_fail():
    svc = CanaryAnalysisService()
    j = svc.compare_error_rates(
        baseline_errors=10, baseline_total=10000,
        canary_errors=500, canary_total=10000)
    assert j.verdict == "fail"
    assert j.canary_value > j.baseline_value


def test_error_rate_insufficient_data():
    svc = CanaryAnalysisService()
    j = svc.compare_error_rates(0, 0, 0, 0)
    assert j.verdict == "inconclusive"


def test_latency_pass():
    svc = CanaryAnalysisService()
    baseline = MetricSample("b", [10, 12, 11, 13, 15, 14, 10, 12, 11, 13])
    canary = MetricSample("c", [11, 13, 12, 14, 16, 15, 11, 13, 12, 14])  # slightly higher
    judgments = svc.compare_latency(baseline, canary)
    # p50 should be within 110% threshold
    p50_j = next(j for j in judgments if "p50" in j.metric)
    assert p50_j.verdict == "pass"


def test_latency_fail():
    svc = CanaryAnalysisService()
    baseline = MetricSample("b", [10] * 100)
    canary = MetricSample("c", [50] * 100)  # 5x slower
    judgments = svc.compare_latency(baseline, canary)
    p50_j = next(j for j in judgments if "p50" in j.metric)
    assert p50_j.verdict == "fail"


def test_full_analysis_pass():
    svc = CanaryAnalysisService()
    result = svc.analyze(
        baseline_errors=5, baseline_total=10000,
        canary_errors=6, canary_total=10000,
        baseline_latency=[10, 12, 11, 13, 15] * 20,
        canary_latency=[11, 13, 12, 14, 16] * 20)
    assert result["overall"] in ("pass", "inconclusive")
    assert "Promote" in result["recommendation"] or "Gather" in result["recommendation"]


def test_full_analysis_fail():
    svc = CanaryAnalysisService()
    result = svc.analyze(
        baseline_errors=5, baseline_total=10000,
        canary_errors=1000, canary_total=10000,
        baseline_latency=[10] * 100,
        canary_latency=[100] * 100)
    assert result["overall"] == "fail"
    assert result["fail_count"] >= 1
    assert "Roll back" in result["recommendation"]


def test_custom_threshold():
    svc = CanaryAnalysisService()
    svc.set_threshold("error_rate", 0.10)  # very lenient
    j = svc.compare_error_rates(
        baseline_errors=100, baseline_total=10000,
        canary_errors=500, canary_total=10000)
    # 5% canary - 1% baseline = 4% diff, still under 10% threshold
    assert j.verdict != "fail"
