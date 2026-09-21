"""Bulk operations tests — schema validation only, no DB needed."""

import pytest
from pydantic import ValidationError

from app.talent.schemas.bulk import (
    BulkCapabilityRequest,
    BulkCapabilityResult,
    BulkError,
    BulkEvidenceRequest,
    BulkTransitionRequest,
    BulkTransitionResult,
    TransitionItem,
    TransitionResult,
)


class TestBulkCapabilityRequest:
    def test_valid_request(self):
        req = BulkCapabilityRequest(
            items=[
                {"canonical_name": "Python", "category": "technical"},
                {"canonical_name": "Java", "category": "technical"},
            ]
        )
        assert len(req.items) == 2

    def test_max_items_exceeded(self):
        items = [{"canonical_name": f"Skill {i}", "category": "technical"} for i in range(101)]
        with pytest.raises(ValidationError, match="Maximum 100"):
            BulkCapabilityRequest(items=items)

    def test_max_items_at_limit(self):
        items = [{"canonical_name": f"Skill {i}", "category": "technical"} for i in range(100)]
        req = BulkCapabilityRequest(items=items)
        assert len(req.items) == 100

    def test_empty_items_rejected(self):
        with pytest.raises(ValidationError):
            BulkCapabilityRequest(items=[])

    def test_invalid_item_in_list(self):
        with pytest.raises(ValidationError):
            BulkCapabilityRequest(items=[{"canonical_name": "", "category": "technical"}])


class TestBulkEvidenceRequest:
    def test_valid_request(self):
        req = BulkEvidenceRequest(
            items=[
                {
                    "capability_id": "cap1",
                    "source_type": "course_completion",
                    "source_id": "course1",
                    "verification_level": "instructor_verified",
                    "occurred_at": "2024-01-01T00:00:00Z",
                },
            ]
        )
        assert len(req.items) == 1

    def test_max_items_exceeded(self):
        items = [
            {
                "capability_id": f"cap{i}",
                "source_type": "course_completion",
                "source_id": f"course{i}",
                "verification_level": "self_reported",
                "occurred_at": "2024-01-01T00:00:00Z",
            }
            for i in range(101)
        ]
        with pytest.raises(ValidationError, match="Maximum 100"):
            BulkEvidenceRequest(items=items)


class TestBulkTransitionRequest:
    def test_valid_request(self):
        req = BulkTransitionRequest(
            transitions=[
                TransitionItem(application_id="app1", status="screening"),
                TransitionItem(application_id="app2", status="rejected", note="Not qualified"),
            ]
        )
        assert len(req.transitions) == 2

    def test_max_transitions_exceeded(self):
        transitions = [
            TransitionItem(application_id=f"app{i}", status="screening") for i in range(51)
        ]
        with pytest.raises(ValidationError, match="Maximum 50"):
            BulkTransitionRequest(transitions=transitions)

    def test_max_at_limit(self):
        transitions = [
            TransitionItem(application_id=f"app{i}", status="screening") for i in range(50)
        ]
        req = BulkTransitionRequest(transitions=transitions)
        assert len(req.transitions) == 50

    def test_empty_transitions_rejected(self):
        with pytest.raises(ValidationError):
            BulkTransitionRequest(transitions=[])


class TestBulkCapabilityResult:
    def test_empty_result(self):
        result = BulkCapabilityResult()
        assert result.created == []
        assert result.errors == []

    def test_with_errors(self):
        result = BulkCapabilityResult(
            errors=[
                BulkError(index=0, error="Duplicate name"),
                BulkError(index=2, error="Invalid category"),
            ]
        )
        assert len(result.errors) == 2
        assert result.errors[0].index == 0


class TestBulkTransitionResult:
    def test_mixed_result(self):
        result = BulkTransitionResult(
            transitioned=[
                TransitionResult(
                    application_id="app1",
                    from_status="submitted",
                    to_status="screening",
                ),
            ],
            errors=[
                BulkError(index=1, error="Invalid transition"),
            ],
        )
        assert len(result.transitioned) == 1
        assert len(result.errors) == 1

    def test_all_success(self):
        result = BulkTransitionResult(
            transitioned=[
                TransitionResult(
                    application_id=f"app{i}",
                    from_status="submitted",
                    to_status="screening",
                )
                for i in range(5)
            ]
        )
        assert len(result.transitioned) == 5
        assert result.errors == []


class TestTransitionItem:
    def test_with_note(self):
        item = TransitionItem(
            application_id="app1",
            status="rejected",
            note="Does not meet requirements",
        )
        assert item.note == "Does not meet requirements"

    def test_without_note(self):
        item = TransitionItem(application_id="app1", status="screening")
        assert item.note is None

    def test_empty_status_rejected(self):
        with pytest.raises(ValidationError):
            TransitionItem(application_id="app1", status="")
