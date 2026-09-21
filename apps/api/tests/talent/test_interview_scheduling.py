"""Interview scheduling tests — slot proposals, acceptance, .ics generation."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.talent.models.interview_slot import SLOT_STATUSES
from app.talent.schemas.interview_slot import (
    InterviewSlotResponse,
    ProposeSlotRequest,
    ProposeSlotsRequest,
)
from app.talent.services.interview_scheduling import (
    _SLOT_TRANSITIONS,
    MAX_SLOTS_PER_STAGE,
    InterviewSchedulingService,
)

# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------


class TestProposeSlotRequest:
    def test_valid_slot(self):
        now = datetime.now(UTC)
        slot = ProposeSlotRequest(
            start_time=now,
            end_time=now + timedelta(hours=1),
            timezone="America/New_York",
        )
        assert slot.timezone == "America/New_York"

    def test_end_before_start_rejected(self):
        now = datetime.now(UTC)
        with pytest.raises(ValidationError, match="end_time must be after"):
            ProposeSlotRequest(
                start_time=now,
                end_time=now - timedelta(hours=1),
                timezone="UTC",
            )

    def test_equal_start_end_rejected(self):
        now = datetime.now(UTC)
        with pytest.raises(ValidationError, match="end_time must be after"):
            ProposeSlotRequest(
                start_time=now,
                end_time=now,
                timezone="UTC",
            )

    def test_meeting_url_max_length(self):
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            ProposeSlotRequest(
                start_time=now,
                end_time=now + timedelta(hours=1),
                timezone="UTC",
                meeting_url="x" * 501,
            )

    def test_timezone_max_length(self):
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            ProposeSlotRequest(
                start_time=now,
                end_time=now + timedelta(hours=1),
                timezone="x" * 51,
            )

    def test_meeting_notes_optional(self):
        now = datetime.now(UTC)
        slot = ProposeSlotRequest(
            start_time=now,
            end_time=now + timedelta(hours=1),
            timezone="UTC",
            meeting_notes="Bring portfolio",
        )
        assert slot.meeting_notes == "Bring portfolio"


class TestProposeSlotsRequest:
    def test_empty_slots_rejected(self):
        with pytest.raises(ValidationError, match="At least one slot"):
            ProposeSlotsRequest(slots=[])

    def test_too_many_slots_rejected(self):
        now = datetime.now(UTC)
        slots = [
            ProposeSlotRequest(
                start_time=now + timedelta(hours=i),
                end_time=now + timedelta(hours=i + 1),
                timezone="UTC",
            )
            for i in range(6)
        ]
        with pytest.raises(ValidationError, match="Maximum 5"):
            ProposeSlotsRequest(slots=slots)

    def test_valid_multiple_slots(self):
        now = datetime.now(UTC)
        slots = [
            ProposeSlotRequest(
                start_time=now + timedelta(hours=i),
                end_time=now + timedelta(hours=i + 1),
                timezone="UTC",
            )
            for i in range(5)
        ]
        req = ProposeSlotsRequest(slots=slots)
        assert len(req.slots) == 5


class TestInterviewSlotResponse:
    def test_from_attributes(self):
        assert InterviewSlotResponse.model_config.get("from_attributes") is True


# ---------------------------------------------------------------------------
# Service logic tests (pure, no DB)
# ---------------------------------------------------------------------------


class TestICSGeneration:
    def test_ics_format(self):
        start = datetime(2026, 9, 15, 14, 0, 0)
        end = datetime(2026, 9, 15, 15, 0, 0)
        ics = InterviewSchedulingService.generate_ics(
            start_time=start,
            end_time=end,
            summary="Interview: AI Designer",
            description="Technical round",
            location="https://zoom.us/j/123",
        )
        assert ics.startswith("BEGIN:VCALENDAR")
        assert "BEGIN:VEVENT" in ics
        assert "END:VEVENT" in ics
        assert ics.strip().endswith("END:VCALENDAR")

    def test_ics_date_format(self):
        start = datetime(2026, 9, 15, 14, 30, 0)
        end = datetime(2026, 9, 15, 15, 30, 0)
        ics = InterviewSchedulingService.generate_ics(
            start_time=start,
            end_time=end,
            summary="Test",
        )
        assert "DTSTART:20260915T143000Z" in ics
        assert "DTEND:20260915T153000Z" in ics

    def test_ics_summary(self):
        start = datetime(2026, 9, 15, 14, 0, 0)
        end = datetime(2026, 9, 15, 15, 0, 0)
        ics = InterviewSchedulingService.generate_ics(
            start_time=start,
            end_time=end,
            summary="Interview: Senior Developer",
        )
        assert "SUMMARY:Interview: Senior Developer" in ics

    def test_ics_location(self):
        start = datetime(2026, 9, 15, 14, 0, 0)
        end = datetime(2026, 9, 15, 15, 0, 0)
        ics = InterviewSchedulingService.generate_ics(
            start_time=start,
            end_time=end,
            summary="Test",
            location="https://meet.google.com/abc-defg-hij",
        )
        assert "LOCATION:https://meet.google.com/abc-defg-hij" in ics

    def test_ics_empty_defaults(self):
        start = datetime(2026, 9, 15, 14, 0, 0)
        end = datetime(2026, 9, 15, 15, 0, 0)
        ics = InterviewSchedulingService.generate_ics(
            start_time=start,
            end_time=end,
            summary="Minimal",
        )
        assert "DESCRIPTION:" in ics
        assert "LOCATION:" in ics

    def test_ics_version(self):
        start = datetime(2026, 9, 15, 14, 0, 0)
        end = datetime(2026, 9, 15, 15, 0, 0)
        ics = InterviewSchedulingService.generate_ics(
            start_time=start,
            end_time=end,
            summary="Test",
        )
        assert "VERSION:2.0" in ics
        assert "PRODID:-//OpenSkill Studio" in ics


# ---------------------------------------------------------------------------
# Model / constants tests
# ---------------------------------------------------------------------------


class TestSlotStatuses:
    def test_all_statuses_present(self):
        assert "proposed" in SLOT_STATUSES
        assert "accepted" in SLOT_STATUSES
        assert "declined" in SLOT_STATUSES
        assert "cancelled" in SLOT_STATUSES

    def test_four_statuses(self):
        assert len(SLOT_STATUSES) == 4


class TestSlotTransitions:
    def test_proposed_can_accept(self):
        assert "accepted" in _SLOT_TRANSITIONS["proposed"]

    def test_proposed_can_decline(self):
        assert "declined" in _SLOT_TRANSITIONS["proposed"]

    def test_proposed_can_cancel(self):
        assert "cancelled" in _SLOT_TRANSITIONS["proposed"]

    def test_accepted_can_cancel(self):
        assert "cancelled" in _SLOT_TRANSITIONS["accepted"]

    def test_declined_is_terminal(self):
        assert len(_SLOT_TRANSITIONS["declined"]) == 0

    def test_cancelled_is_terminal(self):
        assert len(_SLOT_TRANSITIONS["cancelled"]) == 0


class TestConstants:
    def test_max_slots_per_stage(self):
        assert MAX_SLOTS_PER_STAGE == 5
