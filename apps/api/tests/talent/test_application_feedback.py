"""Application feedback tests — schema validation and constants."""

import pytest
from pydantic import ValidationError

from app.talent.models.application import FEEDBACK_TYPES, FEEDBACK_VISIBILITY
from app.talent.schemas.application import (
    CreateFeedbackRequest,
    FeedbackResponse,
    UpdateFeedbackVisibilityRequest,
)


class TestFeedbackConstants:
    def test_feedback_types(self):
        assert "rejection_reason" in FEEDBACK_TYPES
        assert "interview_feedback" in FEEDBACK_TYPES
        assert "general" in FEEDBACK_TYPES
        assert len(FEEDBACK_TYPES) == 3

    def test_visibility_options(self):
        assert "employer_only" in FEEDBACK_VISIBILITY
        assert "shared_with_candidate" in FEEDBACK_VISIBILITY
        assert len(FEEDBACK_VISIBILITY) == 2


class TestCreateFeedbackRequest:
    def test_valid_request(self):
        req = CreateFeedbackRequest(
            feedback_type="rejection_reason",
            content="Not enough experience for this role",
            visibility="employer_only",
        )
        assert req.feedback_type == "rejection_reason"
        assert req.visibility == "employer_only"

    def test_default_visibility(self):
        req = CreateFeedbackRequest(
            feedback_type="general",
            content="Good candidate for future roles",
        )
        assert req.visibility == "employer_only"

    def test_invalid_feedback_type(self):
        with pytest.raises(ValidationError, match="feedback_type"):
            CreateFeedbackRequest(
                feedback_type="invalid_type",
                content="test",
            )

    def test_invalid_visibility(self):
        with pytest.raises(ValidationError, match="visibility"):
            CreateFeedbackRequest(
                feedback_type="general",
                content="test",
                visibility="public",
            )

    def test_content_required(self):
        with pytest.raises(ValidationError):
            CreateFeedbackRequest(
                feedback_type="general",
                content="",
            )

    def test_content_max_length(self):
        with pytest.raises(ValidationError):
            CreateFeedbackRequest(
                feedback_type="general",
                content="x" * 5001,
            )

    def test_shared_with_candidate_visibility(self):
        req = CreateFeedbackRequest(
            feedback_type="interview_feedback",
            content="Strong technical skills demonstrated",
            visibility="shared_with_candidate",
        )
        assert req.visibility == "shared_with_candidate"


class TestUpdateFeedbackVisibilityRequest:
    def test_valid_update(self):
        req = UpdateFeedbackVisibilityRequest(visibility="shared_with_candidate")
        assert req.visibility == "shared_with_candidate"

    def test_invalid_visibility(self):
        with pytest.raises(ValidationError, match="visibility"):
            UpdateFeedbackVisibilityRequest(visibility="public")


class TestFeedbackResponse:
    def test_from_attributes(self):
        assert FeedbackResponse.model_config.get("from_attributes") is True

    def test_response_fields(self):
        fields = FeedbackResponse.model_fields
        assert "id" in fields
        assert "application_id" in fields
        assert "feedback_type" in fields
        assert "content" in fields
        assert "visibility" in fields
        assert "author_id" in fields
        assert "created_at" in fields
