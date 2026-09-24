"""Security advisory endpoints (ADR-016 §38)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import eco_audit, require_platform_admin
from app.ecosystem.schemas import AdvisoryResponse, CreateAdvisoryRequest
from app.ecosystem.services.advisories import AdvisoryService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem/security", tags=["Ecosystem — Security"])


@router.post("/advisories", response_model=DataResponse[AdvisoryResponse], status_code=201)
async def create_advisory(
    body: CreateAdvisoryRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """Register a structured advisory — emits ONE security change event that
    rides the normal fan-out. Never blocks or migrates anything by itself."""
    advisory = await AdvisoryService(db).create(created_by=user.id, **body.model_dump())
    await eco_audit(
        db, user, action="eco.advisory_registered", target_type="eco_security_advisory",
        target_id=advisory.id,
        after={"ref": advisory.advisory_ref, "severity": advisory.severity},
    )
    await db.commit()
    return {"data": advisory}


@router.get("/advisories", response_model=DataResponse[list[AdvisoryResponse]])
async def list_advisories(
    status: str | None = None,
    severity: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {
        "data": await AdvisoryService(db).list(status=status, severity=severity, limit=limit)
    }


@router.get("/advisories/{advisory_id}/affected", response_model=DataResponse[list])
async def advisory_affected(
    advisory_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Resolved affected entities — version_in_range fails OPEN (unknown ≠ safe)."""
    return {"data": await AdvisoryService(db).affected_entities(advisory_id, limit=limit)}


@router.post("/advisories/{advisory_id}/status", response_model=DataResponse[AdvisoryResponse])
async def transition_advisory(
    advisory_id: str,
    to_status: str = Query(..., max_length=20),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    advisory = await AdvisoryService(db).transition(
        advisory_id, to_status=to_status, actor_id=user.id
    )
    await eco_audit(
        db, user, action="eco.advisory_status", target_type="eco_security_advisory",
        target_id=advisory_id, after={"status": to_status},
    )
    await db.commit()
    return {"data": advisory}
