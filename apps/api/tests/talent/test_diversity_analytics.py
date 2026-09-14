"""Diversity analytics tests — pure logic, no DB needed."""

from app.talent.services.diversity_analytics import (
    MIN_COHORT_SIZE,
    PIPELINE_STAGES,
    DiversityAnalyticsService,
)

svc = DiversityAnalyticsService()


class TestStageDropoffs:
    def test_normal_funnel(self):
        stages = {"submitted": 100, "screening": 80, "interview": 40, "assessment": 20, "offer": 10, "hired": 8}
        dropoffs = svc.compute_stage_dropoffs(stages)
        assert len(dropoffs) == 5
        assert dropoffs[0].from_stage == "submitted"
        assert dropoffs[0].drop_off_rate == 0.2

    def test_empty_stages(self):
        dropoffs = svc.compute_stage_dropoffs({})
        assert all(d.total_entered == 0 for d in dropoffs)

    def test_perfect_conversion(self):
        stages = {s: 50 for s in PIPELINE_STAGES}
        dropoffs = svc.compute_stage_dropoffs(stages)
        assert all(d.drop_off_rate == 0.0 for d in dropoffs)


class TestSourceEffectiveness:
    def test_multiple_sources(self):
        apps = [
            {"source": "platform_match", "status": "hired"},
            {"source": "platform_match", "status": "rejected"},
            {"source": "direct_apply", "status": "screening"},
            {"source": "direct_apply", "status": "hired"},
        ]
        results = svc.compute_source_effectiveness(apps)
        assert len(results) == 2
        match_src = next(r for r in results if r.source == "platform_match")
        assert match_src.hire_rate == 0.5

    def test_empty_applications(self):
        results = svc.compute_source_effectiveness([])
        assert results == []


class TestEquityFlags:
    def test_high_dropoff_flagged(self):
        from app.talent.services.diversity_analytics import StageDropoff
        dropoffs = [
            StageDropoff("screening", "interview", 50, 5, 0.9, None, None),
        ]
        flags = svc.compute_equity_flags(dropoffs, [])
        assert len(flags) == 1
        assert "90%" in flags[0]

    def test_source_disparity_flagged(self):
        from app.talent.services.diversity_analytics import SourceEffectiveness
        sources = [
            SourceEffectiveness("match", 20, 0.5, 0.3, 0.2, None),
            SourceEffectiveness("direct", 20, 0.5, 0.05, 0.02, None),
        ]
        flags = svc.compute_equity_flags([], sources)
        assert any("disparity" in f.lower() for f in flags)

    def test_no_flags_when_fair(self):
        from app.talent.services.diversity_analytics import SourceEffectiveness, StageDropoff
        dropoffs = [StageDropoff("s", "i", 50, 35, 0.3, None, None)]
        sources = [
            SourceEffectiveness("a", 20, 0.5, 0.3, 0.15, None),
            SourceEffectiveness("b", 20, 0.5, 0.3, 0.12, None),
        ]
        flags = svc.compute_equity_flags(dropoffs, sources)
        assert len(flags) == 0


class TestBuildReport:
    def test_full_report(self):
        apps = [
            {"source": "match", "status": "hired"},
            {"source": "match", "status": "rejected"},
        ]
        stages = {"submitted": 10, "screening": 8, "interview": 5, "assessment": 3, "offer": 2, "hired": 1}
        report = svc.build_report(
            org_id="o1", applications=apps,
            applications_by_stage=stages,
        )
        assert report.total_applications == 2
        assert len(report.stage_dropoffs) == 5
        assert len(report.source_effectiveness) == 1


class TestConstants:
    def test_min_cohort(self):
        assert MIN_COHORT_SIZE == 10

    def test_pipeline_stages(self):
        assert PIPELINE_STAGES[0] == "submitted"
        assert PIPELINE_STAGES[-1] == "hired"
