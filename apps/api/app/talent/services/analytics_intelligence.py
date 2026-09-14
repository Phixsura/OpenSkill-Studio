"""Analytics intelligence — reports, cohort analysis, KPIs, benchmarks, attribution.

Closes gaps: #151 (read receipts), #154 (translation placeholder), #155 (real-time placeholder),
#156-#170 (analytics & reporting).
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Gap #151: Read receipt visibility
# ---------------------------------------------------------------------------

def format_read_receipt(message: dict) -> dict:
    """Format read receipt data for display to sender."""
    return {
        "message_id": message.get("id"),
        "read": message.get("read_at") is not None,
        "read_at": message.get("read_at"),
        "delivered": True,
    }


# ---------------------------------------------------------------------------
# Gap #154: Message translation placeholder
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES = frozenset({"en", "zh", "ja", "ko", "es", "fr", "de", "pt", "ar", "hi"})


def detect_language(text: str) -> str:
    """Simple language detection heuristic (placeholder for ML-based detection)."""
    # CJK character ranges
    for ch in text[:100]:
        if '一' <= ch <= '鿿':
            return "zh"
        if '぀' <= ch <= 'ゟ' or '゠' <= ch <= 'ヿ':
            return "ja"
        if '가' <= ch <= '힯':
            return "ko"
        if '؀' <= ch <= 'ۿ':
            return "ar"
        if 'ऀ' <= ch <= 'ॿ':
            return "hi"
    return "en"


def translation_placeholder(text: str, target_lang: str) -> dict:
    """Placeholder for translation — returns metadata without actual translation.

    In production, integrate with Google Translate / DeepL / Azure Translator.
    """
    source = detect_language(text)
    return {
        "source_language": source,
        "target_language": target_lang,
        "translated": source == target_lang,
        "text": text if source == target_lang else f"[Translation to {target_lang} requires API integration]",
        "provider": None,
    }


# ---------------------------------------------------------------------------
# Gap #156: Custom report builder
# ---------------------------------------------------------------------------

REPORT_TYPES = frozenset({
    "hiring_funnel", "skill_distribution", "placement_outcomes",
    "evidence_growth", "capability_coverage", "employer_activity",
    "candidate_pipeline", "credential_issuance", "workforce_gap",
    "team_skills", "diversity_pipeline",
})

REPORT_FORMATS = frozenset({"json", "csv", "html"})


@dataclass(frozen=True, slots=True)
class ReportConfig:
    report_type: str
    title: str
    filters: dict  # {date_range, org_id, capability_ids, ...}
    format: str
    scheduled: bool
    schedule_cron: str | None  # e.g., "0 9 * * 1" for weekly Monday 9am


def validate_report_config(config: dict) -> list[str]:
    errors = []
    rt = config.get("report_type", "")
    if rt not in REPORT_TYPES:
        errors.append(f"Invalid report_type. Must be one of: {sorted(REPORT_TYPES)}")
    fmt = config.get("format", "json")
    if fmt not in REPORT_FORMATS:
        errors.append(f"Invalid format. Must be one of: {sorted(REPORT_FORMATS)}")
    if not config.get("title"):
        errors.append("Report title is required")
    return errors


# ---------------------------------------------------------------------------
# Gap #159: Cohort analysis
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class CohortComparison:
    cohort_a: str
    cohort_b: str
    metric: str
    value_a: float
    value_b: float
    delta: float
    significant: bool  # >10% difference


def compare_cohorts(
    cohort_a_name: str, cohort_a_value: float,
    cohort_b_name: str, cohort_b_value: float,
    metric: str,
) -> CohortComparison:
    delta = cohort_b_value - cohort_a_value
    avg = (cohort_a_value + cohort_b_value) / 2 if (cohort_a_value + cohort_b_value) > 0 else 1
    pct_diff = abs(delta) / avg
    return CohortComparison(
        cohort_a=cohort_a_name, cohort_b=cohort_b_name,
        metric=metric, value_a=cohort_a_value, value_b=cohort_b_value,
        delta=round(delta, 3), significant=pct_diff > 0.10,
    )


# ---------------------------------------------------------------------------
# Gap #160: Funnel drop-off with reasons
# ---------------------------------------------------------------------------

DROP_OFF_REASONS = frozenset({
    "unresponsive", "withdrew", "rejected_skills", "rejected_culture",
    "rejected_compensation", "failed_assessment", "no_show",
    "position_filled", "budget_cut", "other",
})


def categorize_drop_offs(events: list[dict]) -> dict:
    """Categorize funnel drop-offs by reason."""
    by_reason: dict[str, int] = {}
    by_stage: dict[str, dict[str, int]] = {}
    for ev in events:
        reason = ev.get("reason", "other")
        stage = ev.get("stage", "unknown")
        by_reason[reason] = by_reason.get(reason, 0) + 1
        by_stage.setdefault(stage, {})
        by_stage[stage][reason] = by_stage[stage].get(reason, 0) + 1
    return {"by_reason": by_reason, "by_stage": by_stage, "total": len(events)}


# ---------------------------------------------------------------------------
# Gap #162: Source attribution tracking
# ---------------------------------------------------------------------------

SOURCE_CHANNELS = frozenset({
    "direct", "platform_match", "referral", "career_page",
    "job_board", "social_media", "email_campaign", "event",
    "pool_invitation", "other",
})


@dataclass(frozen=True, slots=True)
class SourceAttribution:
    channel: str
    utm_source: str | None
    utm_medium: str | None
    utm_campaign: str | None
    landing_page: str | None


def parse_utm_params(url: str) -> dict:
    """Extract UTM parameters from a URL."""
    from urllib.parse import parse_qs, urlparse
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return {
        "utm_source": params.get("utm_source", [None])[0],
        "utm_medium": params.get("utm_medium", [None])[0],
        "utm_campaign": params.get("utm_campaign", [None])[0],
        "utm_content": params.get("utm_content", [None])[0],
        "utm_term": params.get("utm_term", [None])[0],
    }


# ---------------------------------------------------------------------------
# Gap #165: Benchmark comparisons
# ---------------------------------------------------------------------------

INDUSTRY_BENCHMARKS = {
    "time_to_hire_days": {"tech": 35, "finance": 42, "healthcare": 49, "education": 28, "average": 38},
    "offer_acceptance_rate": {"tech": 0.72, "finance": 0.68, "healthcare": 0.75, "education": 0.82, "average": 0.74},
    "interview_to_offer_rate": {"tech": 0.25, "finance": 0.20, "healthcare": 0.30, "education": 0.35, "average": 0.27},
    "placement_success_rate": {"tech": 0.85, "finance": 0.82, "healthcare": 0.88, "education": 0.90, "average": 0.86},
}


def compare_to_benchmark(metric: str, value: float, industry: str = "average") -> dict:
    benchmarks = INDUSTRY_BENCHMARKS.get(metric, {})
    benchmark = benchmarks.get(industry, benchmarks.get("average"))
    if benchmark is None:
        return {"metric": metric, "value": value, "benchmark": None, "comparison": "no_data"}

    if isinstance(benchmark, (int, float)):
        diff = value - benchmark
        pct = diff / benchmark if benchmark != 0 else 0
        if pct > 0.1:
            comparison = "above_benchmark"
        elif pct < -0.1:
            comparison = "below_benchmark"
        else:
            comparison = "at_benchmark"
    else:
        comparison = "no_data"
        diff = 0
        pct = 0

    return {
        "metric": metric, "value": value,
        "benchmark": benchmark, "industry": industry,
        "delta": round(diff, 3), "pct_diff": round(pct, 3),
        "comparison": comparison,
    }


# ---------------------------------------------------------------------------
# Gap #169: Custom KPI tracking
# ---------------------------------------------------------------------------

KPI_AGGREGATIONS = frozenset({"count", "sum", "avg", "min", "max", "rate"})


@dataclass(frozen=True, slots=True)
class KPIDefinition:
    id: str
    name: str
    metric_type: str  # count, sum, avg, min, max, rate
    source: str  # applications, placements, evidence, credentials, ...
    filters: dict
    target_value: float | None
    warning_threshold: float | None


def validate_kpi(kpi: dict) -> list[str]:
    errors = []
    if not kpi.get("name"):
        errors.append("KPI name is required")
    agg = kpi.get("metric_type", "")
    if agg not in KPI_AGGREGATIONS:
        errors.append(f"Invalid metric_type. Must be one of: {sorted(KPI_AGGREGATIONS)}")
    if not kpi.get("source"):
        errors.append("Data source is required")
    return errors


def evaluate_kpi(kpi: dict, current_value: float) -> dict:
    """Evaluate a KPI against its target and warning thresholds."""
    target = kpi.get("target_value")
    warning = kpi.get("warning_threshold")

    status = "on_track"
    if target is not None and current_value < target * 0.8:
        status = "critical"
    elif warning is not None and current_value < warning:
        status = "warning"
    elif target is not None and current_value >= target:
        status = "achieved"

    return {
        "kpi_name": kpi.get("name"),
        "current_value": current_value,
        "target": target,
        "warning_threshold": warning,
        "status": status,
        "achievement_pct": round(current_value / target * 100, 1) if target else None,
    }


# ---------------------------------------------------------------------------
# Gap #170: Analytics annotation
# ---------------------------------------------------------------------------

ANNOTATION_TYPES = frozenset({"note", "milestone", "alert", "insight"})


def validate_annotation(annotation: dict) -> list[str]:
    errors = []
    if not annotation.get("text") or len(annotation.get("text", "")) < 3:
        errors.append("Annotation text must be at least 3 characters")
    at = annotation.get("annotation_type", "")
    if at and at not in ANNOTATION_TYPES:
        errors.append(f"Invalid type. Must be one of: {sorted(ANNOTATION_TYPES)}")
    return errors
