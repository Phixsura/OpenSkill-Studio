"""Career goal tests — user-side goal tracking (N3)."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.talent.models.career_goal import GOAL_STATUSES, MAX_ACTIVE_GOALS
from app.talent.schemas.career_goal import (
    CreateGoalRequest,
    GoalProgressResponse,
    GoalResponse,
    UpdateGoalRequest,
)
from app.talent.services.career_goals import _days_remaining


class TestGoalConstants:
    def test_statuses(self):
        assert "active" in GOAL_STATUSES
        assert "completed" in GOAL_STATUSES
        assert "abandoned" in GOAL_STATUSES

    def test_max_active_goals(self):
        assert MAX_ACTIVE_GOALS == 5


class TestCreateGoalRequest:
    def test_valid_request(self):
        req = CreateGoalRequest(
            title="Become Senior AI Designer",
            target_role="Senior AI Visual Designer",
        )
        assert req.title == "Become Senior AI Designer"
        assert req.target_capabilities is None
        assert req.target_date is None

    def test_with_capabilities(self):
        req = CreateGoalRequest(
            title="Master AI Visual",
            target_capabilities=[
                {"capability_id": "cap1", "target_level": 4},
                {"capability_id": "cap2", "target_level": 3},
            ],
        )
        assert len(req.target_capabilities) == 2

    def test_with_target_date(self):
        req = CreateGoalRequest(
            title="Q1 Goal",
            target_date=date(2027, 3, 31),
        )
        assert req.target_date == date(2027, 3, 31)

    def test_title_max_length(self):
        # 200 chars should work
        req = CreateGoalRequest(title="A" * 200)
        assert len(req.title) == 200

    def test_title_too_long(self):
        with pytest.raises(ValidationError):
            CreateGoalRequest(title="A" * 201)

    def test_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            CreateGoalRequest(title="")


class TestUpdateGoalRequest:
    def test_partial(self):
        req = UpdateGoalRequest(title="Updated Goal")
        assert req.title == "Updated Goal"
        assert req.description is None

    def test_update_date(self):
        req = UpdateGoalRequest(target_date=date(2027, 6, 30))
        assert req.target_date == date(2027, 6, 30)


class TestGoalResponse:
    def test_from_attributes(self):
        assert GoalResponse.model_config.get("from_attributes") is True


class TestGoalProgressResponse:
    def test_full_progress(self):
        progress = GoalProgressResponse(
            goal_id="goal1",
            title="Master AI",
            overall_progress=100.0,
            target_date=None,
            days_remaining=None,
            capabilities=[
                {
                    "capability_id": "cap1",
                    "capability_name": "AI Design",
                    "current_level": 4,
                    "target_level": 4,
                    "progress": 100.0,
                    "met": True,
                }
            ],
        )
        assert progress.overall_progress == 100.0

    def test_partial_progress(self):
        progress = GoalProgressResponse(
            goal_id="goal1",
            title="Learning Path",
            overall_progress=50.0,
            target_date=date(2027, 1, 1),
            days_remaining=100,
            capabilities=[
                {
                    "capability_id": "cap1",
                    "current_level": 2,
                    "target_level": 4,
                    "progress": 50.0,
                    "met": False,
                }
            ],
        )
        assert progress.overall_progress == 50.0
        assert progress.days_remaining == 100


class TestDaysRemaining:
    def test_no_date(self):
        assert _days_remaining(None) is None

    def test_future_date(self):
        future = date.today() + timedelta(days=30)
        result = _days_remaining(future)
        assert result is not None
        assert 29 <= result <= 30

    def test_past_date(self):
        past = date.today() - timedelta(days=5)
        assert _days_remaining(past) == 0

    def test_today(self):
        assert _days_remaining(date.today()) == 0
