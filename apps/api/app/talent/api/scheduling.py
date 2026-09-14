"""Interview scheduling API — time slot proposals, acceptance, and .ics calendar invites.

Authorization:
  - Propose slots: employer org member of the opportunity
  - List slots: employer org member OR the applicant
  - Accept/decline: only the applicant
  - Cancel: employer org member OR applicant
  - Calendar .ics: employer org member OR applicant
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.application import Application, InterviewStage
from app.talent.models.employer import Opportunity
from app.talent.models.interview_slot import InterviewSlot
from app.talent.schemas.interview_slot import (
    InterviewSlotResponse,
    ProposeSlotsRequest,
)

router = APIRouter(prefix="/talent", tags=["Talent — Interview Scheduling"])


async def _load_stage_context(
    db: AsyncSession, interview_id: str
) -> tuple[InterviewStage, Application, Opportunity]:
    """Load interview stage + application + opportunity, or raise 404."""
    stage = await db.get(InterviewStage, interview_id)
    if not stage:
        raise HTTPException(404, "Interview stage not found")
    app = await db.get(Application, stage.application_id)
    if not app:
        raise HTTPException(404, "Application not found")
    opp = await db.get(Opportunity, app.opportunity_id)
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    return stage, app, opp


async def _load_slot_context(
    db: AsyncSession, slot_id: str
) -> tuple[InterviewSlot, InterviewStage, Application, Opportunity]:
    """Load slot + stage + application + opportunity, or raise 404."""
    slot = await db.get(InterviewSlot, slot_id)
    if not slot:
        raise HTTPException(404, "Interview slot not found")
    stage, app, opp = await _load_stage_context(db, slot.interview_stage_id)
    return slot, stage, app, opp


@router.post(
    "/interviews/{interview_id}/slots",
    response_model=DataResponse[list[InterviewSlotResponse]],
    status_code=201,
)
async def propose_slots(
    interview_id: str,
    body: ProposeSlotsRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Propose time slots for an interview — employer org member only."""
    stage, app, opp = await _load_stage_context(db, interview_id)
    await require_org_member(opp.employer_org_id, user, db)

    from app.talent.services.interview_scheduling import InterviewSchedulingService

    svc = InterviewSchedulingService(db)
    try:
        slots = await svc.propose_slots(
            interview_stage_id=interview_id,
            proposed_by=user.id,
            slots=[s.model_dump() for s in body.slots],
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from None

    await db.commit()
    for s in slots:
        await db.refresh(s)
    return DataResponse(
        data=[InterviewSlotResponse.model_validate(s) for s in slots]
    )


@router.get(
    "/interviews/{interview_id}/slots",
    response_model=DataResponse[list[InterviewSlotResponse]],
)
async def list_slots(
    interview_id: str,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List proposed slots — employer org member or applicant."""
    stage, app, opp = await _load_stage_context(db, interview_id)

    # Auth: employer org member OR the applicant
    if app.user_id != user.id:
        await require_org_member(opp.employer_org_id, user, db)

    from app.talent.services.interview_scheduling import InterviewSchedulingService

    svc = InterviewSchedulingService(db)
    slots = await svc.list_slots(interview_id, status=status)
    return DataResponse(
        data=[InterviewSlotResponse.model_validate(s) for s in slots]
    )


@router.post(
    "/interview-slots/{slot_id}/accept",
    response_model=DataResponse[InterviewSlotResponse],
)
async def accept_slot(
    slot_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Accept a proposed time slot — applicant only.

    Automatically declines all other proposed slots for the same stage
    and updates InterviewStage.scheduled_at.
    """
    slot, stage, app, opp = await _load_slot_context(db, slot_id)

    # Only the applicant can accept
    if app.user_id != user.id:
        raise HTTPException(403, "Only the applicant can accept interview slots")

    from app.talent.services.interview_scheduling import InterviewSchedulingService

    svc = InterviewSchedulingService(db)
    result = await svc.accept_slot(slot_id, user.id)
    if not result:
        raise HTTPException(422, "Slot cannot be accepted (not in proposed status)")

    await db.commit()
    await db.refresh(result)
    return DataResponse(data=InterviewSlotResponse.model_validate(result))


@router.post(
    "/interview-slots/{slot_id}/decline",
    response_model=DataResponse[InterviewSlotResponse],
)
async def decline_slot(
    slot_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Decline a proposed time slot — applicant only."""
    slot, stage, app, opp = await _load_slot_context(db, slot_id)

    if app.user_id != user.id:
        raise HTTPException(403, "Only the applicant can decline interview slots")

    from app.talent.services.interview_scheduling import InterviewSchedulingService

    svc = InterviewSchedulingService(db)
    result = await svc.decline_slot(slot_id, user.id)
    if not result:
        raise HTTPException(422, "Slot cannot be declined (not in proposed status)")

    await db.commit()
    await db.refresh(result)
    return DataResponse(data=InterviewSlotResponse.model_validate(result))


@router.post(
    "/interview-slots/{slot_id}/cancel",
    response_model=DataResponse[InterviewSlotResponse],
)
async def cancel_slot(
    slot_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Cancel a proposed or accepted slot — employer org member or applicant."""
    slot, stage, app, opp = await _load_slot_context(db, slot_id)

    # Either the applicant or employer org member can cancel
    if app.user_id != user.id:
        await require_org_member(opp.employer_org_id, user, db)

    from app.talent.services.interview_scheduling import InterviewSchedulingService

    svc = InterviewSchedulingService(db)
    result = await svc.cancel_slot(slot_id, user.id)
    if not result:
        raise HTTPException(
            422, "Slot cannot be cancelled (already declined or cancelled)"
        )

    await db.commit()
    await db.refresh(result)
    return DataResponse(data=InterviewSlotResponse.model_validate(result))


@router.get("/interview-slots/{slot_id}/calendar.ics")
async def download_calendar_invite(
    slot_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Download .ics calendar invite for an accepted slot.

    Only available for accepted slots. Accessible by employer org member
    or the applicant.
    """
    slot, stage, app, opp = await _load_slot_context(db, slot_id)

    # Auth: employer org member OR the applicant
    if app.user_id != user.id:
        await require_org_member(opp.employer_org_id, user, db)

    from app.talent.services.interview_scheduling import InterviewSchedulingService

    svc = InterviewSchedulingService(db)
    ics_content = await svc.get_calendar_invite(slot_id)
    if not ics_content:
        raise HTTPException(
            422, "Calendar invite only available for accepted slots"
        )

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="interview-{slot_id}.ics"'
        },
    )


# ---- Gap #51: Question bank ----

@router.get("/talent/question-bank/templates", response_model=DataResponse[list[str]])
async def list_rubric_template_names(
    user: User = Depends(get_current_user),
):
    """List available rubric templates."""
    from app.talent.services.interview_intelligence import list_rubric_templates
    return DataResponse(data=list_rubric_templates())


@router.get("/talent/question-bank/templates/{name}", response_model=DataResponse[dict])
async def get_rubric_template_endpoint(
    name: str,
    user: User = Depends(get_current_user),
):
    """Get a rubric template by name."""
    from app.talent.services.interview_intelligence import get_rubric_template
    template = get_rubric_template(name)
    if not template:
        raise HTTPException(404, "Template not found")
    return DataResponse(data=template)


# ---- Gap #97: Availability validation ----

@router.post("/talent/interviewer-availability/validate", response_model=DataResponse[dict])
async def validate_availability_endpoint(
    body: dict,
    user: User = Depends(get_current_user),
):
    """Validate interviewer availability slots."""
    from app.talent.services.interview_intelligence import validate_availability
    errors = validate_availability(body.get("slots", []))
    return DataResponse(data={"valid": len(errors) == 0, "errors": errors})


# ---- Gap #98: Booking link ----

@router.get("/talent/interviews/{interview_id}/booking-link", response_model=DataResponse[dict])
async def get_booking_link(
    interview_id: str,
    user: User = Depends(get_current_user),
):
    """Generate a self-scheduling booking link for candidates."""
    from app.talent.services.interview_intelligence import generate_booking_link
    return DataResponse(data=generate_booking_link(interview_id))


# ---- Gap #99: Reminders ----

@router.get("/talent/interviews/{interview_id}/reminders", response_model=DataResponse[list[dict]])
async def get_interview_reminders(
    interview_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get scheduled reminder times for an interview."""
    from sqlalchemy import select as sa_select

    from app.talent.models.interview_slot import InterviewSlot
    from app.talent.services.interview_intelligence import compute_reminder_schedule
    result = await db.execute(
        sa_select(InterviewSlot).where(InterviewSlot.interview_stage_id == interview_id, InterviewSlot.status == "accepted")
    )
    slot = result.scalar_one_or_none()
    if not slot:
        return DataResponse(data=[])
    reminders = compute_reminder_schedule(slot.start_time)
    return DataResponse(data=reminders)


# ---- Gap #59: Credential renewal ----

@router.get("/talent/credentials/{credential_id}/renewal-eligibility", response_model=DataResponse[dict])
async def check_credential_renewal(
    credential_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Check if a credential is eligible for renewal."""
    from app.talent.models.assessment import Credential
    from app.talent.services.interview_intelligence import check_renewal_eligibility
    cred = await db.get(Credential, credential_id)
    if not cred:
        raise HTTPException(404, "Credential not found")
    result = check_renewal_eligibility({
        "expires_at": cred.expires_at.isoformat() if cred.expires_at else None,
        "revalidation_at": cred.revalidation_at.isoformat() if cred.revalidation_at else None,
    })
    return DataResponse(data=result)
