"""Application pipeline tests — state machine, structural enforcement."""

import pytest

from app.talent.models.application import APPLICATION_TRANSITIONS, TERMINAL_STATUSES


class TestApplicationStateMachine:
    def test_all_statuses_have_transitions(self):
        expected_statuses = {
            "draft",
            "submitted",
            "screening",
            "interview",
            "assessment",
            "offer",
            "accepted",
            "rejected",
            "withdrawn",
            "hired",
            "completed",
        }
        assert set(APPLICATION_TRANSITIONS.keys()) == expected_statuses

    def test_terminal_statuses_have_no_transitions(self):
        for status in TERMINAL_STATUSES:
            assert APPLICATION_TRANSITIONS[status] == []

    def test_rejected_is_terminal(self):
        assert "rejected" in TERMINAL_STATUSES

    def test_withdrawn_is_terminal(self):
        assert "withdrawn" in TERMINAL_STATUSES

    def test_completed_is_terminal(self):
        assert "completed" in TERMINAL_STATUSES

    def test_offer_can_be_accepted_or_rejected(self):
        transitions = APPLICATION_TRANSITIONS["offer"]
        assert "accepted" in transitions
        assert "rejected" in transitions

    def test_no_auto_hire_transition(self):
        """There is no state that auto-transitions to hired.
        hired requires explicit transition from accepted."""
        for status, targets in APPLICATION_TRANSITIONS.items():
            if status == "accepted":
                assert "hired" in targets
            else:
                assert "hired" not in targets

    def test_offer_to_accepted(self):
        """Candidates must be able to accept offers."""
        assert "accepted" in APPLICATION_TRANSITIONS["offer"]

    def test_accepted_is_candidate_transition(self):
        """Only the candidate (not the employer) can accept an offer."""
        from app.talent.api.applications import _CANDIDATE_TRANSITIONS

        assert "accepted" in _CANDIDATE_TRANSITIONS

    def test_draft_to_submitted(self):
        assert "submitted" in APPLICATION_TRANSITIONS["draft"]

    def test_screening_to_interview(self):
        assert "interview" in APPLICATION_TRANSITIONS["screening"]

    def test_hired_to_completed(self):
        assert "completed" in APPLICATION_TRANSITIONS["hired"]


# ---- API tests ----


@pytest.mark.asyncio
async def test_list_applications_requires_auth(client):
    response = await client.get("/api/v1/talent/applications")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_apply_requires_auth(client):
    response = await client.post("/api/v1/talent/opportunities/fake/apply", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_transition_requires_auth(client):
    response = await client.patch(
        "/api/v1/talent/applications/fake/status",
        json={"status": "screening"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_placements_requires_auth(client):
    response = await client.get("/api/v1/talent/placements")
    assert response.status_code == 401
