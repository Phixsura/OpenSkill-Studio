"""Diversity analytics — demographic-free pipeline analysis for bias detection.

IMPORTANT: This service does NOT use protected attributes (race, gender, etc.).
It analyzes pipeline patterns that may indicate systemic issues:
  - Stage drop-off rates (are certain stages disproportionately filtering?)
  - Source effectiveness (do different application sources have different outcomes?)
  - Time-in-stage variance (are some applications stuck longer than others?)
  - Cohort comparison (do graduates from different programs have equal outcomes?)

These are structural signals, not individual-level demographic analysis.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StageDropoff:
    """Drop-off analysis per pipeline stage."""
    from_stage: str
    to_stage: str
    total_entered: int
    total_progressed: int
    drop_off_rate: float  # 0-1
    avg_days_in_stage: float | None
    variance_days: float | None  # high variance may indicate inconsistency


@dataclass(frozen=True, slots=True)
class SourceEffectiveness:
    """Application source effectiveness analysis."""
    source: str  # platform_match, direct_apply, referral, pool_invitation
    total_applications: int
    interview_rate: float
    offer_rate: float
    hire_rate: float
    avg_time_to_hire_days: float | None


@dataclass(frozen=True, slots=True)
class CohortOutcomeComparison:
    """Compare outcomes across cohorts/programs (privacy-safe aggregate)."""
    cohort_id: str
    cohort_name: str
    sample_size: int
    placement_rate: float
    avg_time_to_placement_days: float | None
    employer_verification_rate: float
    suppressed: bool  # True if sample < min_cohort


@dataclass(frozen=True, slots=True)
class PipelineEquityReport:
    """Full pipeline equity analysis."""
    opportunity_id: str | None
    org_id: str | None
    analysis_period_days: int
    total_applications: int
    stage_dropoffs: list[StageDropoff]
    source_effectiveness: list[SourceEffectiveness]
    cohort_comparisons: list[CohortOutcomeComparison]
    equity_flags: list[str]  # human-readable concerns


PIPELINE_STAGES = [
    "submitted", "screening", "interview", "assessment", "offer", "hired",
]

MIN_COHORT_SIZE = 10


class DiversityAnalyticsService:
    def compute_stage_dropoffs(
        self, applications_by_stage: dict[str, int],
    ) -> list[StageDropoff]:
        """Compute drop-off between consecutive stages."""
        dropoffs = []
        for i in range(len(PIPELINE_STAGES) - 1):
            from_stage = PIPELINE_STAGES[i]
            to_stage = PIPELINE_STAGES[i + 1]
            entered = applications_by_stage.get(from_stage, 0)
            progressed = applications_by_stage.get(to_stage, 0)
            rate = 1.0 - (progressed / entered) if entered > 0 else 0.0

            dropoffs.append(StageDropoff(
                from_stage=from_stage,
                to_stage=to_stage,
                total_entered=entered,
                total_progressed=progressed,
                drop_off_rate=round(rate, 3),
                avg_days_in_stage=None,
                variance_days=None,
            ))
        return dropoffs

    def compute_source_effectiveness(
        self, applications: list[dict],
    ) -> list[SourceEffectiveness]:
        """Analyze effectiveness by application source."""
        by_source: dict[str, dict] = {}
        for app in applications:
            src = app.get("source", "direct_apply")
            if src not in by_source:
                by_source[src] = {"total": 0, "interview": 0, "offer": 0, "hire": 0}
            by_source[src]["total"] += 1
            status = app.get("status", "")
            if status in ("interview", "assessment", "offer", "accepted", "hired", "completed"):
                by_source[src]["interview"] += 1
            if status in ("offer", "accepted", "hired", "completed"):
                by_source[src]["offer"] += 1
            if status in ("hired", "completed"):
                by_source[src]["hire"] += 1

        results = []
        for src, data in by_source.items():
            total = data["total"]
            results.append(SourceEffectiveness(
                source=src,
                total_applications=total,
                interview_rate=round(data["interview"] / total, 3) if total else 0.0,
                offer_rate=round(data["offer"] / total, 3) if total else 0.0,
                hire_rate=round(data["hire"] / total, 3) if total else 0.0,
                avg_time_to_hire_days=None,
            ))
        return results

    def compute_equity_flags(
        self,
        dropoffs: list[StageDropoff],
        sources: list[SourceEffectiveness],
    ) -> list[str]:
        """Identify potential equity concerns."""
        flags = []

        # Flag stages with >80% drop-off
        for d in dropoffs:
            if d.drop_off_rate > 0.80 and d.total_entered >= 10:
                flags.append(
                    f"High drop-off at {d.from_stage}→{d.to_stage}: "
                    f"{d.drop_off_rate:.0%} ({d.total_entered}→{d.total_progressed})"
                )

        # Flag source disparity >2x
        if len(sources) >= 2:
            hire_rates = [(s.source, s.hire_rate) for s in sources if s.total_applications >= 5]
            if hire_rates:
                max_rate = max(r for _, r in hire_rates)
                min_rate = min(r for _, r in hire_rates)
                if max_rate > 0 and min_rate > 0 and max_rate / min_rate > 2.0:
                    flags.append(
                        f"Source disparity: hire rates range from {min_rate:.0%} to {max_rate:.0%}"
                    )

        return flags

    def build_report(
        self,
        *,
        opportunity_id: str | None = None,
        org_id: str | None = None,
        applications: list[dict],
        applications_by_stage: dict[str, int],
        analysis_period_days: int = 90,
    ) -> PipelineEquityReport:
        dropoffs = self.compute_stage_dropoffs(applications_by_stage)
        sources = self.compute_source_effectiveness(applications)
        flags = self.compute_equity_flags(dropoffs, sources)

        return PipelineEquityReport(
            opportunity_id=opportunity_id,
            org_id=org_id,
            analysis_period_days=analysis_period_days,
            total_applications=len(applications),
            stage_dropoffs=dropoffs,
            source_effectiveness=sources,
            cohort_comparisons=[],
            equity_flags=flags,
        )
