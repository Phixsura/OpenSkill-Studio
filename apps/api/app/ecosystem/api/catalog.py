"""Canonical catalog + resolution + lifecycle endpoints (Parts C, L)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import require_platform_admin
from app.ecosystem.schemas import (
    BulkDecideRequest,
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


@router.post(
    "/catalog/{segment}/{entity_id}/merge-into/{target_id}",
    response_model=DataResponse[dict],
)
async def merge_catalog_entity(
    segment: str,
    entity_id: str,
    target_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """§13 registry dedupe: merge a duplicate canonical entity into the
    survivor — re-points all references, retires the duplicate with a
    supersedes audit edge. Nothing historical is lost."""
    outcome = await CatalogService(db).merge_entities(
        _kind(segment), entity_id, target_id, actor_id=user.id
    )
    await db.commit()
    return {"data": outcome}


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


@router.get("/deprecation-calendar.ics", include_in_schema=True)
async def deprecation_calendar_ics(
    within_days: int = Query(365, ge=1, le=730),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """iCalendar feed of upcoming sunsets — subscribe from any calendar app
    (endoflife.date's signature integration surface, §13)."""
    from fastapi.responses import Response

    sunsets = await LifecycleService(db).upcoming_sunsets(within_days=within_days)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OpenSkill Studio//Ecosystem Intelligence//EN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:AI Ecosystem Deprecation Calendar",
    ]
    for item in sunsets:
        sunset_at = item["sunset_at"]
        day = sunset_at.strftime("%Y%m%d")
        # Escape per RFC 5545 (commas/semicolons/backslashes in names)
        name = (
            str(item["name"]).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
        )[:200]
        lines += [
            "BEGIN:VEVENT",
            f"UID:eco-sunset-{item['entity_id']}@openskill",
            f"DTSTART;VALUE=DATE:{day}",
            f"SUMMARY:Sunset: {name}",
            f"DESCRIPTION:{item['entity_kind']} reaches end of life "
            f"(lifecycle: {item['lifecycle_status']})",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return Response(
        content="\r\n".join(lines) + "\r\n",
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="eco-deprecations.ics"'},
    )


@router.get("/export", response_model=dict)
async def catalog_export(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """One canonical, machine-readable catalog document (§13) — the LiteLLM
    `model_prices_and_context_window.json` / deps.dev-dataset posture: the
    catalog IS an integration currency. Content-hashed for cache validation
    and downstream drift detection; approved prices only, never raw
    observations."""
    import hashlib
    import json
    from datetime import UTC, datetime

    from app.ecosystem.models.mapping import CapabilityMapping, PriceObservation

    svc = CatalogService(db)
    entities: dict = {}
    for segment, kind in _KIND_SEGMENTS.items():
        rows, _total = await svc.list_entities(kind, limit=100, offset=0)
        entities[segment] = [
            CatalogEntityResponse.model_validate(r).model_dump(mode="json") for r in rows
        ]
    mappings = [
        MappingResponse.model_validate(m).model_dump(mode="json")
        for m in await db.scalars(select(CapabilityMapping).limit(2000))
    ]
    prices = [
        {
            "entity_kind": p.entity_kind,
            "entity_id": p.entity_id,
            "unit": p.unit,
            "price": float(p.price),
            "currency": p.currency,
            "region": p.region,
        }
        for p in await db.scalars(
            select(PriceObservation)
            .where(PriceObservation.reconciliation_status == "approved")
            .limit(2000)
        )
    ]
    body = {"entities": entities, "capability_mappings": mappings, "approved_prices": prices}
    content_hash = hashlib.sha256(
        json.dumps(body, sort_keys=True, default=str).encode()
    ).hexdigest()
    return {
        "data": {
            "schema": "openskill.eco.catalog/v1",
            "generated_at": datetime.now(UTC).isoformat(),
            "content_hash": content_hash,
            **body,
        }
    }


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


@router.post("/resolution-candidates/bulk-decide", response_model=DataResponse[dict])
async def bulk_decide_resolution(
    body: BulkDecideRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """ADR-016 §11.1 — per-id outcomes; one bad id never aborts the batch."""
    if body.decision not in ("confirm", "reject"):
        raise AppError("VALIDATION_ERROR", f"Unknown decision: {body.decision}", 422)
    svc = ResolutionService(db)
    decided: list[dict] = []
    failed: list[dict] = []
    for candidate_id in body.ids:
        try:
            if body.decision == "confirm":
                _, entity_id = await svc.confirm(candidate_id, actor_id=user.id)
                decided.append({"id": candidate_id, "entity_id": entity_id})
            else:
                await svc.reject(candidate_id, actor_id=user.id)
                decided.append({"id": candidate_id})
        except AppError as exc:
            failed.append({"id": candidate_id, "error_code": exc.code})
    await db.commit()
    return {"data": {"decision": body.decision, "decided": decided, "failed": failed}}


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
