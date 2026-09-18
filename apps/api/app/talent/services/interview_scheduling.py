"""Interview scheduling service — time slot proposals, acceptance, and .ics generation.

Workflow:
  1. Employer proposes 1-5 time slots for an interview stage
  2. Candidate views proposed slots and accepts one (or declines all)
  3. Accepting a slot auto-declines remaining proposals and updates the stage
  4. Either party can cancel an accepted slot
  5. .ics calendar invites can be downloaded for accepted slots
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import Application, InterviewStage
from app.talent.models.employer import Opportunity
from app.talent.models.interview_slot import InterviewSlot

# Maximum proposals per interview stage
MAX_SLOTS_PER_STAGE = 5

# Valid slot status transitions
_SLOT_TRANSITIONS: dict[str, set[str]] = {
    "proposed": {"accepted", "declined", "cancelled"},
    "accepted": {"cancelled"},
    "declined": set(),
    "cancelled": set(),
}

ICS_TEMPLATE = """\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OpenSkill Studio//Interview Scheduling//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
DTSTART:{start}
DTEND:{end}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""


def _ics_escape(v: str) -> str:
    """Sanitize a string for safe inclusion in an iCalendar TEXT property.

    Per RFC 5545 §3.3.11: escape backslash, comma, semicolon, and replace
    newlines with literal \\n. Strip CR to prevent CRLF injection.
    """
    return (
        v.replace("\\", "\\\\")
        .replace("\r", "")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


class InterviewSchedulingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def propose_slots(
        self,
        interview_stage_id: str,
        proposed_by: str,
        slots: list[dict],
    ) -> list[InterviewSlot]:
        """Propose one or more time slots for an interview.

        Args:
            interview_stage_id: The interview stage to schedule.
            proposed_by: User proposing the times (employer-side).
            slots: List of {start_time, end_time, timezone, meeting_url?, meeting_notes?}.

        Raises:
            ValueError: If too many slots or invalid times.
        """
        if not slots:
            raise ValueError("At least one slot is required")
        if len(slots) > MAX_SLOTS_PER_STAGE:
            raise ValueError(f"Maximum {MAX_SLOTS_PER_STAGE} slots per proposal")

        # Check existing proposed slots for this stage
        existing_q = select(InterviewSlot).where(
            InterviewSlot.interview_stage_id == interview_stage_id,
            InterviewSlot.status == "proposed",
        )
        existing = (await self.db.execute(existing_q)).scalars().all()
        total = len(existing) + len(slots)
        if total > MAX_SLOTS_PER_STAGE:
            raise ValueError(
                f"Too many proposed slots ({total}). "
                f"Maximum is {MAX_SLOTS_PER_STAGE} including existing proposals."
            )

        created: list[InterviewSlot] = []
        for s in slots:
            start = s["start_time"]
            end = s["end_time"]
            if end <= start:
                raise ValueError(f"end_time ({end}) must be after start_time ({start})")

            slot = InterviewSlot(
                interview_stage_id=interview_stage_id,
                proposed_by=proposed_by,
                start_time=start,
                end_time=end,
                timezone=s.get("timezone", "UTC"),
                meeting_url=s.get("meeting_url"),
                meeting_notes=s.get("meeting_notes"),
                status="proposed",
            )
            self.db.add(slot)
            created.append(slot)

        await self.db.flush()
        return created

    async def accept_slot(self, slot_id: str, user_id: str) -> InterviewSlot | None:
        """Accept a proposed slot.

        Automatically declines all other proposed slots for the same stage
        and updates the InterviewStage.scheduled_at.
        """
        slot = await self.db.get(InterviewSlot, slot_id)
        if not slot or slot.status != "proposed":
            return None

        slot.status = "accepted"
        slot.accepted_by = user_id
        slot.accepted_at = datetime.now(UTC)

        # Decline all other proposed slots for this stage
        await self.db.execute(
            update(InterviewSlot)
            .where(
                InterviewSlot.interview_stage_id == slot.interview_stage_id,
                InterviewSlot.id != slot_id,
                InterviewSlot.status == "proposed",
            )
            .values(status="declined")
        )

        # Update the interview stage with the scheduled time
        stage = await self.db.get(InterviewStage, slot.interview_stage_id)
        if stage:
            stage.scheduled_at = slot.start_time
            stage.scheduled_timezone = slot.timezone
            stage.meeting_url = slot.meeting_url

        await self.db.flush()
        return slot

    async def decline_slot(self, slot_id: str, user_id: str) -> InterviewSlot | None:
        """Decline a specific proposed slot."""
        slot = await self.db.get(InterviewSlot, slot_id)
        if not slot or slot.status != "proposed":
            return None

        slot.status = "declined"
        await self.db.flush()
        return slot

    async def cancel_slot(self, slot_id: str, user_id: str) -> InterviewSlot | None:
        """Cancel an accepted or proposed slot."""
        slot = await self.db.get(InterviewSlot, slot_id)
        if not slot:
            return None
        if slot.status not in ("proposed", "accepted"):
            return None

        was_accepted = slot.status == "accepted"
        slot.status = "cancelled"

        # If cancelling an accepted slot, clear the stage scheduled time
        if was_accepted:
            stage = await self.db.get(InterviewStage, slot.interview_stage_id)
            if stage:
                stage.scheduled_at = None
                stage.scheduled_timezone = None
                stage.meeting_url = None

        await self.db.flush()
        return slot

    async def list_slots(
        self,
        interview_stage_id: str,
        *,
        status: str | None = None,
    ) -> list[InterviewSlot]:
        """List all slots for an interview stage."""
        q = select(InterviewSlot).where(InterviewSlot.interview_stage_id == interview_stage_id)
        if status:
            q = q.where(InterviewSlot.status == status)
        q = q.order_by(InterviewSlot.start_time)

        result = await self.db.execute(q)
        return list(result.scalars().all())

    @staticmethod
    def generate_ics(
        *,
        start_time: datetime,
        end_time: datetime,
        summary: str,
        description: str = "",
        location: str = "",
    ) -> str:
        """Generate an .ics calendar invite string.

        Dates are formatted as YYYYMMDDTHHMMSSZ (UTC).
        """
        start_str = start_time.strftime("%Y%m%dT%H%M%SZ")
        end_str = end_time.strftime("%Y%m%dT%H%M%SZ")
        return ICS_TEMPLATE.format(
            start=start_str,
            end=end_str,
            summary=_ics_escape(summary),
            description=_ics_escape(description),
            location=_ics_escape(location),
        )

    async def get_calendar_invite(self, slot_id: str) -> str | None:
        """Generate .ics content for an accepted slot.

        Returns None if slot is not accepted or not found.
        """
        slot = await self.db.get(InterviewSlot, slot_id)
        if not slot or slot.status != "accepted":
            return None

        stage = await self.db.get(InterviewStage, slot.interview_stage_id)
        if not stage:
            return None

        app = await self.db.get(Application, stage.application_id)
        opp = await self.db.get(Opportunity, app.opportunity_id) if app else None

        summary = f"Interview: {opp.title}" if opp else "Interview"
        description = f"Stage: {stage.stage_type}"
        if stage.application_id:
            description += f"\\nApplication: {stage.application_id}"
        location = slot.meeting_url or ""

        return self.generate_ics(
            start_time=slot.start_time,
            end_time=slot.end_time,
            summary=summary,
            description=description,
            location=location,
        )
