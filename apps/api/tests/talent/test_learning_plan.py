"""Learning plan tests — pure logic, no DB needed."""

from app.talent.services.learning_plan import (
    ContentRecommendation,
    LearningRecommendation,
)


class TestLearningRecommendation:
    def test_dataclass_fields(self):
        rec = LearningRecommendation(
            capability_id="cap1",
            capability_name="Python",
            current_level=1,
            target_level=3,
            gap_size=2,
            recommended_content=[
                ContentRecommendation(
                    source_type="skill_pack",
                    source_id="sp1",
                    coverage_weight=0.8,
                ),
            ],
        )
        assert rec.gap_size == 2
        assert len(rec.recommended_content) == 1
        assert rec.recommended_content[0].source_type == "skill_pack"

    def test_frozen(self):
        rec = LearningRecommendation(
            capability_id="cap1",
            capability_name="Python",
            current_level=1,
            target_level=3,
            gap_size=2,
            recommended_content=[],
        )
        try:
            rec.gap_size = 5  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass


class TestContentRecommendation:
    def test_fields(self):
        cr = ContentRecommendation(
            source_type="assessment_blueprint",
            source_id="ab1",
            coverage_weight=0.5,
        )
        assert cr.source_type == "assessment_blueprint"
        assert cr.coverage_weight == 0.5

    def test_frozen(self):
        cr = ContentRecommendation(
            source_type="skill",
            source_id="s1",
            coverage_weight=1.0,
        )
        try:
            cr.source_type = "other"  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass
