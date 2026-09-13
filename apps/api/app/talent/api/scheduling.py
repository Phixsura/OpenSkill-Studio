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
