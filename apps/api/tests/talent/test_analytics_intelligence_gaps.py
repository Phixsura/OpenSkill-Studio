"""Tests for gaps #151-170: Analytics & Reporting Intelligence."""

from app.talent.services.analytics_intelligence import (
    ANNOTATION_TYPES,
    DROP_OFF_REASONS,
    INDUSTRY_BENCHMARKS,
    KPI_AGGREGATIONS,
    REPORT_FORMATS,
    REPORT_TYPES,
    SOURCE_CHANNELS,
    SUPPORTED_LANGUAGES,
    categorize_drop_offs,
    compare_cohorts,
    compare_to_benchmark,
    detect_language,
    evaluate_kpi,
    format_read_receipt,
    parse_utm_params,
    translation_placeholder,
    validate_annotation,
    validate_kpi,
    validate_report_config,
)


class TestReadReceipt:
    def test_read(self):
        msg = {"id": "m1", "read_at": "2026-01-01T10:00:00"}
        r = format_read_receipt(msg)
        assert r["read"] is True

    def test_unread(self):
        r = format_read_receipt({"id": "m1", "read_at": None})
        assert r["read"] is False


class TestTranslation:
    def test_detect_english(self):
        assert detect_language("Hello world") == "en"

    def test_detect_chinese(self):
        assert detect_language("你好世界") == "zh"

    def test_placeholder(self):
        result = translation_placeholder("Hello", "zh")
        assert result["source_language"] == "en"
        assert result["target_language"] == "zh"

    def test_languages(self):
        assert len(SUPPORTED_LANGUAGES) >= 8


class TestReportBuilder:
    def test_valid(self):
        config = {"report_type": "hiring_funnel", "title": "Q3 Report", "format": "json"}
        assert validate_report_config(config) == []

    def test_invalid_type(self):
        errors = validate_report_config({"report_type": "invalid", "title": "R"})
        assert len(errors) > 0

    def test_types(self):
        assert len(REPORT_TYPES) >= 10
        assert len(REPORT_FORMATS) == 3


class TestCohortAnalysis:
    def test_significant(self):
        result = compare_cohorts("2025 Fall", 0.85, "2026 Spring", 0.65, "placement_rate")
        assert result.significant is True
        assert result.delta < 0

    def test_not_significant(self):
        result = compare_cohorts("A", 0.80, "B", 0.82, "pass_rate")
        assert result.significant is False


class TestDropOffReasons:
    def test_categorize(self):
        events = [
            {"stage": "screening", "reason": "unresponsive"},
            {"stage": "screening", "reason": "unresponsive"},
            {"stage": "interview", "reason": "no_show"},
        ]
        result = categorize_drop_offs(events)
        assert result["total"] == 3
        assert result["by_reason"]["unresponsive"] == 2

    def test_reasons(self):
        assert "unresponsive" in DROP_OFF_REASONS
        assert len(DROP_OFF_REASONS) >= 8


class TestSourceAttribution:
    def test_parse_utm(self):
        url = "https://example.com?utm_source=linkedin&utm_medium=social&utm_campaign=q3_hiring"
        params = parse_utm_params(url)
        assert params["utm_source"] == "linkedin"
        assert params["utm_campaign"] == "q3_hiring"

    def test_no_utm(self):
        params = parse_utm_params("https://example.com/jobs")
        assert params["utm_source"] is None

    def test_channels(self):
        assert "referral" in SOURCE_CHANNELS
        assert len(SOURCE_CHANNELS) >= 8


class TestBenchmarks:
    def test_above(self):
        result = compare_to_benchmark("time_to_hire_days", 25, "tech")
        assert result["comparison"] == "below_benchmark"  # 25 < 35 is good for time

    def test_at(self):
        result = compare_to_benchmark("offer_acceptance_rate", 0.74, "average")
        assert result["comparison"] == "at_benchmark"

    def test_no_data(self):
        result = compare_to_benchmark("nonexistent", 50)
        assert result["comparison"] == "no_data"

    def test_industries(self):
        assert "time_to_hire_days" in INDUSTRY_BENCHMARKS


class TestKPI:
    def test_valid(self):
        kpi = {"name": "Hire Rate", "metric_type": "rate", "source": "applications"}
        assert validate_kpi(kpi) == []

    def test_invalid_type(self):
        errors = validate_kpi({"name": "X", "metric_type": "invalid", "source": "x"})
        assert len(errors) > 0

    def test_evaluate_achieved(self):
        result = evaluate_kpi({"name": "Hires", "target_value": 10, "warning_threshold": 7}, 12)
        assert result["status"] == "achieved"

    def test_evaluate_warning(self):
        result = evaluate_kpi({"name": "Hires", "target_value": 10, "warning_threshold": 9}, 8.5)
        assert result["status"] == "warning"

    def test_evaluate_critical(self):
        result = evaluate_kpi({"name": "Hires", "target_value": 10, "warning_threshold": 7}, 3)
        assert result["status"] == "critical"

    def test_aggregations(self):
        assert len(KPI_AGGREGATIONS) >= 5


class TestAnnotations:
    def test_valid(self):
        assert validate_annotation({"text": "Important note", "annotation_type": "note"}) == []

    def test_short(self):
        errors = validate_annotation({"text": "Hi"})
        assert len(errors) > 0

    def test_types(self):
        assert len(ANNOTATION_TYPES) == 4
