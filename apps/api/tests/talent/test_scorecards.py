"""Structured interview scorecard tests — schema validation, no DB needed."""

import pytest
from pydantic import ValidationError

from app.talent.models.scorecard import RECOMMENDATIONS
from app.talent.schemas.scorecard import (
    VALID_RECOMMENDATIONS,
    CreateScorecardRequest,
    CreateScorecardTemplateRequest,
    CriterionItem,
    ScorecardResponse,
    ScorecardTemplateResponse,
    UpdateScorecardRequest,
    UpdateScorecardTemplateRequest,
)


class TestCriterionItem:
    def test_valid(self):
        c = CriterionItem(name="Technical Skills", weight=0.4, rubric="1-5 scale")
        assert c.name == "Technical Skills"
        assert c.weight == 0.4

    def test_weight_zero_invalid(self):
        with pytest.raises(ValidationError, match="weight"):
            CriterionItem(name="X", weight=0)

    def test_weight_negative_invalid(self):
        with pytest.raises(ValidationError, match="weight"):
            CriterionItem(name="X", weight=-0.5)

    def test_weight_over_one_invalid(self):
        with pytest.raises(ValidationError, match="weight"):
            CriterionItem(name="X", weight=1.5)

    def test_weight_one_valid(self):
        c = CriterionItem(name="X", weight=1.0)
        assert c.weight == 1.0

    def test_default_weight(self):
        c = CriterionItem(name="X")
        assert c.weight == 1.0


class TestCreateScorecardTemplateRequest:
    def test_minimal(self):
        req = CreateScorecardTemplateRequest(name="Engineering Interview")
        assert req.name == "Engineering Interview"
        assert req.criteria == []

    def test_with_criteria(self):
        req = CreateScorecardTemplateRequest(
            name="Test",
            criteria=[
                CriterionItem(name="A", weight=0.5),
                CriterionItem(name="B", weight=0.5),
            ],
        )
        assert len(req.criteria) == 2


class TestUpdateScorecardTemplateRequest:
    def test_valid_status(self):
        req = UpdateScorecardTemplateRequest(status="archived")
        assert req.status == "archived"

    def test_invalid_status(self):
        with pytest.raises(ValidationError, match="status"):
            UpdateScorecardTemplateRequest(status="deleted")


class TestCreateScorecardRequest:
    def test_minimal(self):
        req = CreateScorecardRequest()
        assert req.ratings == {}
        assert req.overall_rating is None

    def test_valid_recommendation(self):
        req = CreateScorecardRequest(recommendation="strong_hire")
        assert req.recommendation == "strong_hire"

    def test_invalid_recommendation(self):
        with pytest.raises(ValidationError, match="recommendation"):
            CreateScorecardRequest(recommendation="maybe")

    def test_overall_rating_valid_range(self):
        for rating in range(1, 6):
            req = CreateScorecardRequest(overall_rating=rating)
            assert req.overall_rating == rating

    def test_overall_rating_zero_invalid(self):
        with pytest.raises(ValidationError, match="overall_rating"):
            CreateScorecardRequest(overall_rating=0)

    def test_overall_rating_six_invalid(self):
        with pytest.raises(ValidationError, match="overall_rating"):
            CreateScorecardRequest(overall_rating=6)

    def test_with_ratings_dict(self):
        req = CreateScorecardRequest(
            ratings={
                "Technical Skills": {"score": 4, "notes": "Strong"},
                "Communication": {"score": 3, "notes": "OK"},
            },
            overall_rating=4,
            recommendation="hire",
        )
        assert "Technical Skills" in req.ratings
        assert req.overall_rating == 4


class TestUpdateScorecardRequest:
    def test_partial_update(self):
        req = UpdateScorecardRequest(overall_rating=5)
        assert req.overall_rating == 5
        assert req.recommendation is None

    def test_invalid_rating(self):
        with pytest.raises(ValidationError, match="overall_rating"):
            UpdateScorecardRequest(overall_rating=10)

    def test_invalid_recommendation(self):
        with pytest.raises(ValidationError, match="recommendation"):
            UpdateScorecardRequest(recommendation="unsure")


class TestScorecardResponse:
    def test_from_dict(self):
        resp = ScorecardResponse(
            id="01J000000000000000000000A1",
            interview_stage_id="01J000000000000000000000B1",
            interviewer_id="01J000000000000000000000C1",
            ratings={"X": {"score": 4}},
            overall_rating=4,
            recommendation="hire",
        )
        assert resp.id.startswith("01J")


class TestScorecardTemplateResponse:
    def test_from_dict(self):
        resp = ScorecardTemplateResponse(
            id="01J000000000000000000000A1",
            org_id="01J000000000000000000000B1",
            name="Test Template",
            status="active",
        )
        assert resp.name == "Test Template"


class TestConstants:
    def test_model_recommendations(self):
        assert "strong_hire" in RECOMMENDATIONS
        assert "strong_no_hire" in RECOMMENDATIONS
        assert len(RECOMMENDATIONS) == 4

    def test_schema_recommendations_match_model(self):
        assert VALID_RECOMMENDATIONS == RECOMMENDATIONS

    def test_all_valid_recommendations(self):
        for rec in VALID_RECOMMENDATIONS:
            req = CreateScorecardRequest(recommendation=rec)
            assert req.recommendation == rec
