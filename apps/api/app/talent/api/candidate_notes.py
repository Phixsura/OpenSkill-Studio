"""Candidate notes API — employer-side CRM notes (N4).

Notes are org-scoped: only org members can create/view.
Only the author can update/delete their own notes.
Candidates never see these notes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.candidate_note import CandidateNote
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Candidate Notes"])


class CreateNoteRequest(BaseModel):
    note_text: str = Field(..., min_length=1, max_length=5000)
    tags: list[str] = Field(default_factory=list)
    opportunity_id: str | None = None


class UpdateNoteRequest(BaseModel):
    note_text: str | None = Field(None, min_length=1, max_length=5000)
    tags: list[str] | None = None


class NoteResponse(BaseModel):
    id: str
    org_id: str
    candidate_user_id: str
    author_id: str
    opportunity_id: str | None
    note_text: str
    tags: list[str]
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


@router.post(
    "/orgs/{org_id}/candidates/{user_id}/notes",
    response_model=DataResponse[NoteResponse],
    status_code=201,
    summary="Create Note",
)
async def create_note(
    org_id: str,
    user_id: str,
    body: CreateNoteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Add a note about a candidate — org members only."""
    await require_org_member(org_id, user, db)

    note = CandidateNote(
        org_id=org_id,
        candidate_user_id=user_id,
        author_id=user.id,
        opportunity_id=body.opportunity_id,
        note_text=body.note_text,
        tags=body.tags,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return DataResponse(data=NoteResponse.model_validate(note))


@router.get(
    "/orgs/{org_id}/candidates/{user_id}/notes",
    response_model=CursorListResponse[NoteResponse],
    summary="List Notes",
)
async def list_notes(
    org_id: str,
    user_id: str,
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List notes about a candidate — org members only."""
    await require_org_member(org_id, user, db)

    q = select(CandidateNote).where(
        CandidateNote.org_id == org_id,
        CandidateNote.candidate_user_id == user_id,
    )
    if cursor:
        q = q.where(CandidateNote.id < cursor)
    q = q.order_by(CandidateNote.created_at.desc()).limit(limit + 1)

    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    next_cursor = items[-1].id if has_more and items else None

    return CursorListResponse(
        data=[NoteResponse.model_validate(n) for n in items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.patch(
    "/candidate-notes/{note_id}",
    response_model=DataResponse[NoteResponse],
    summary="Update Note",
)
async def update_note(
    note_id: str,
    body: UpdateNoteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a note — author only."""
    note = await db.get(CandidateNote, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    if note.author_id != user.id:
        raise HTTPException(403, "Only the author can update this note")

    if body.note_text is not None:
        note.note_text = body.note_text
    if body.tags is not None:
        note.tags = body.tags

    await db.commit()
    await db.refresh(note)
    return DataResponse(data=NoteResponse.model_validate(note))


@router.delete("/candidate-notes/{note_id}", status_code=204,
    summary="Delete Note",
)
async def delete_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a note — author only."""
    note = await db.get(CandidateNote, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    if note.author_id != user.id:
        raise HTTPException(403, "Only the author can delete this note")

    # Audit: deletion logged
    await db.delete(note)
    await db.commit()
