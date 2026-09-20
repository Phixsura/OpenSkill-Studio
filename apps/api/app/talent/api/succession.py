from app.talent.schemas.requests import AnalyticsBody

"""Succession planning API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.succession import KeyRole, SuccessorNomination
from app.talent.schemas.cursor import CursorListResponse, CursorMeta

router = APIRouter(prefix="/talent", tags=["Talent — Succession Planning"])


@router.post("/orgs/{org_id}/key-roles", response_model=DataResponse[dict], status_code=201,
    summary="Create Key Role",
)
async def create_key_role(
    org_id: str,
    body: AnalyticsBody,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create key role."""
    await require_org_member(org_id, user, db)
    kr = KeyRole(
        org_id=org_id,
        title=body.get("title", ""),
        description=body.get("description"),
        required_capabilities=body.get("required_capabilities", []),
        current_holder_id=body.get("current_holder_id"),
        criticality=body.get("criticality", "medium"),
        created_by=user.id,
    )
    db.add(kr)
    await db.commit()
    await db.refresh(kr)
    return DataResponse(data={"id": kr.id, "title": kr.title, "criticality": kr.criticality})


@router.get("/orgs/{org_id}/key-roles", response_model=CursorListResponse[dict],
    summary="List Key Roles",
)
async def list_key_roles(
    org_id: str,
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List key roles."""
    await require_org_member(org_id, user, db)
    q = select(KeyRole).where(KeyRole.org_id == org_id, KeyRole.status == "active")
    if cursor:
        q = q.where(KeyRole.id < cursor)
    q = q.order_by(KeyRole.created_at.desc()).limit(limit + 1)
    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    nc = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[
            {
                "id": r.id,
                "title": r.title,
                "criticality": r.criticality,
                "current_holder_id": r.current_holder_id,
            }
            for r in items
        ],
        meta=CursorMeta(next_cursor=nc, has_more=has_more),
    )


@router.post("/key-roles/{role_id}/nominations", response_model=DataResponse[dict], status_code=201,
    summary="Nominate Successor",
)
async def nominate_successor(
    role_id: str,
    body: AnalyticsBody,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Nominate successor."""
    kr = await db.get(KeyRole, role_id)
    if not kr:
        raise HTTPException(404, "Key role not found")
    await require_org_member(kr.org_id, user, db)
    nom = SuccessorNomination(
        key_role_id=role_id,
        candidate_user_id=body.get("candidate_user_id") or "",
        readiness=body.get("readiness", "not_assessed"),
        nominated_by=user.id,
    )
    db.add(nom)
    await db.commit()
    await db.refresh(nom)
    return DataResponse(
        data={"id": nom.id, "readiness": nom.readiness, "candidate_user_id": nom.candidate_user_id}
    )


@router.get("/key-roles/{role_id}/nominations", response_model=CursorListResponse[dict],
    summary="List Nominations",
)
async def list_nominations(
    role_id: str,
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List nominations."""
    kr = await db.get(KeyRole, role_id)
    if not kr:
        raise HTTPException(404, "Key role not found")
    await require_org_member(kr.org_id, user, db)
    q = select(SuccessorNomination).where(SuccessorNomination.key_role_id == role_id)
    if cursor:
        q = q.where(SuccessorNomination.id < cursor)
    q = q.order_by(SuccessorNomination.created_at.desc()).limit(min(limit + 1, 200))
    result = await db.execute(q)
    items = list(result.scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    nc = items[-1].id if has_more and items else None
    return CursorListResponse(
        data=[
            {
                "id": n.id,
                "candidate_user_id": n.candidate_user_id,
                "readiness": n.readiness,
                "capability_match": n.capability_match,
            }
            for n in items
        ],
        meta=CursorMeta(next_cursor=nc, has_more=has_more),
    )


@router.get("/key-roles/{role_id}/risk", response_model=DataResponse[dict],
    summary="Assess Succession Risk",
)
async def assess_succession_risk(
    role_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """Assess succession risk."""
    kr = await db.get(KeyRole, role_id)
    if not kr:
        raise HTTPException(404, "Key role not found")
    await require_org_member(kr.org_id, user, db)
    q = select(SuccessorNomination).where(SuccessorNomination.key_role_id == role_id)
    result = await db.execute(q)
    noms = result.scalars().all()
    ready_now = sum(1 for n in noms if n.readiness == "ready_now")
    pipeline = len(noms)
    if kr.criticality == "critical" and ready_now == 0:
        risk = "critical"
    elif ready_now == 0 and pipeline > 0:
        risk = "high"
    elif ready_now == 1:
        risk = "medium"
    else:
        risk = "low"
    return DataResponse(
        data={
            "role_id": role_id,
            "title": kr.title,
            "risk_level": risk,
            "ready_now": ready_now,
            "pipeline": pipeline,
        }
    )
