"""Canonical catalog + resolution + lifecycle endpoints (Parts C, L)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import require_platform_admin
from app.ecosystem.schemas import (
    CatalogEntityResponse,
    ConfirmResolutionRequest,
    LifecycleTransitionRequest,
    LifecycleTransitionResponse,
    MappingResponse,
    ResolutionCandidateResponse,
    UpdateCatalogEntityRequest,
    UpsertMappingRequest,
)
from app.ecosystem.services.capability_mapping import CapabilityMappingService
from app.ecosystem.services.catalog import CatalogService, LifecycleService
from app.ecosystem.services.resolution import ResolutionService
from app.exceptions import AppError
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem", tags=["Ecosystem — Catalog"])

# URL segment → entity kind
_KIND_SEGMENTS = {
    "providers": "provider",
    "tools": "tool",
    "models": "model",
    "model-versions": "model_version",
    "workflows": "workflow",
    "agents": "agent",
    "node-packages": "node_package",
}


def _kind(segment: str) -> str:
    kind = _KIND_SEGMENTS.get(segment)
    if kind is None:
        raise AppError("NOT_FOUND", "Unknown catalog kind", 404)
    return kind


@router.get("/catalog/{segment}", response_model=dict)
async def list_catalog(
    segment: str,
    lifecycle_status: str | None = None,
    search: str | None = Query(None, max_length=200),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    rows, total = await CatalogService(db).list_entities(
        _kind(segment), lifecycle_status=lifecycle_status, search=search,
        limit=limit, offset=offset,
    )
    return {
        "data": [CatalogEntityResponse.model_validate(r).model_dump() for r in rows],
        "meta": {"total": total, "limit": limit, "offset": offset},
    }


@router.get("/catalog/{segment}/{entity_id}", response_model=DataResponse[CatalogEntityResponse])
async def get_catalog_entity(
    segment: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await CatalogService(db).get(_kind(segment), entity_id)}


@router.patch("/catalog/{segment}/{entity_id}", response_model=DataResponse[CatalogEntityResponse])
async def update_catalog_entity(
    segment: str,
    entity_id: str,
    body: UpdateCatalogEntityRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    entity = await CatalogService(db).update(
        _kind(segment), entity_id, body.model_dump(exclude_unset=True)
    )
    await db.commit()
    return {"data": entity}


@router.get("/catalog/{segment}/{entity_id}/conflicts", response_model=DataResponse[list])
async def entity_conflicts(
    segment: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Disagreeing sources — both observations retained, conflict surfaced."""
    return {"data": await CatalogService(db).conflicting_observations(_kind(segment), entity_id)}


@router.post(
    "/catalog/{segment}/{entity_id}/lifecycle",
    response_model=DataResponse[CatalogEntityResponse],
)
async def lifecycle_transition(
    segment: str,
    entity_id: str,
    body: LifecycleTransitionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    entity = await LifecycleService(db).transition(
        _kind(segment),
        entity_id,
        to_status=body.to_status,
        reason=body.reason,
        note=body.note,
        actor_id=user.id,
    )
    await db.commit()
    return {"data": entity}


@router.get(
    "/catalog/{segment}/{entity_id}/lifecycle",
    response_model=DataResponse[list[LifecycleTransitionResponse]],
)
async def lifecycle_history(
    segment: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await LifecycleService(db).history(_kind(segment), entity_id)}


@router.get("/deprecation-calendar", response_model=DataResponse[list])
async def deprecation_calendar(
    within_days: int = Query(90, ge=1, le=730),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await LifecycleService(db).upcoming_sunsets(within_days=within_days)}


# ── Entity resolution ───────────────────────────────────────────────


@router.get(
    "/resolution-candidates", response_model=DataResponse[list[ResolutionCandidateResponse]]
)
async def list_resolution_candidates(
    entity_kind: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {
        "data": await ResolutionService(db).list_pending(
            entity_kind=entity_kind, limit=limit, offset=offset
        )
    }


@router.post("/resolution-candidates/{candidate_id}/confirm", response_model=dict)
async def confirm_resolution(
    candidate_id: str,
    body: ConfirmResolutionRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    candidate, entity_id = await ResolutionService(db).confirm(
        candidate_id,
        actor_id=user.id,
        target_entity_id=body.target_entity_id if body else None,
    )
    await db.commit()
    return {
        "data": {
            "candidate": ResolutionCandidateResponse.model_validate(candidate).model_dump(),
            "entity_id": entity_id,
        }
    }


@router.post(
    "/resolution-candidates/{candidate_id}/reject",
    response_model=DataResponse[ResolutionCandidateResponse],
)
async def reject_resolution(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    candidate = await ResolutionService(db).reject(candidate_id, actor_id=user.id)
    await db.commit()
    return {"data": candidate}


# ── Capability mappings (Part D) ────────────────────────────────────


@router.get("/capability-mappings", response_model=DataResponse[list[MappingResponse]])
async def list_mappings(
    entity_kind: str | None = None,
    entity_id: str | None = None,
    capability_key: str | None = None,
    min_evidence: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    svc = CapabilityMappingService(db)
    if capability_key:
        return {
            "data": await svc.list_for_capability(capability_key, min_evidence=min_evidence)
        }
    if entity_kind and entity_id:
        return {"data": await svc.list_for_entity(entity_kind, entity_id)}
    raise AppError(
        "VALIDATION_ERROR", "Filter by capability_key or entity_kind+entity_id", 422
    )


@router.post("/capability-mappings", response_model=DataResponse[MappingResponse])
async def upsert_mapping(
    body: UpsertMappingRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    mapping = await CapabilityMappingService(db).upsert(
        entity_kind=body.entity_kind,
        entity_id=body.entity_id,
        capability_key=body.capability_key,
        evidence_level=body.evidence_level,
        io_spec=body.io_spec,
        confidence=body.confidence,
        source_observation_id=body.source_observation_id,
        actor_id=user.id,
        force=body.force,
        actor_is_admin=True,
    )
    await db.commit()
    return {"data": mapping}
