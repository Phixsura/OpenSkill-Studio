"""Career path prediction tests — pure logic, no DB needed."""

from app.talent.services.career_path import (
    MAX_LEVEL_GAP,
    MAX_REACHABLE_GAPS,
    SkillGap,
    _suggest_action,
)


class TestSuggestAction:
    def test_no_existing_skill_low_target(self):
        action = _suggest_action(0, 2, 2)
        assert "foundational" in action.lower() or "introductory" in action.lower()

    def test_no_existing_skill_high_target(self):
        action = _suggest_action(0, 4, 4)
        assert "introductory" in action.lower() or "start" in action.lower()

    def test_one_level_gap(self):
        action = _suggest_action(2, 3, 1)
        assert "2-3" in action or "evidence" in action.lower()

    def test_two_level_gap(self):
        action = _suggest_action(1, 3, 2)
        assert "assessment" in action.lower() or "evidence" in action.lower()

    def test_large_gap(self):
        action = _suggest_action(1, 4, 3)
        assert "upskilling" in action.lower() or "advancement" in action.lower()


class TestSkillGap:
    def test_immutable(self):
        gap = SkillGap(
            capability_id="cap1",
            capability_name="Python",
            current_level=2,
            required_level=4,
            gap_size=2,
            action="Complete assessment",
        )
        assert gap.capability_id == "cap1"
        assert gap.gap_size == 2

    def test_frozen(self):
        gap = SkillGap(
            capability_id="cap1",
            capability_name="Python",
            current_level=2,
            required_level=4,
            gap_size=2,
            action="Complete assessment",
        )
        try:
            gap.gap_size = 5  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass


class TestConstants:
    def test_max_reachable_gaps(self):
        assert MAX_REACHABLE_GAPS == 3

    def test_max_level_gap(self):
        assert MAX_LEVEL_GAP == 3
