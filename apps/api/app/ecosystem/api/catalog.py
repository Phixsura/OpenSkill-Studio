"""Canonical catalog + resolution + lifecycle endpoints (Parts C, L)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import eco_audit, require_platform_admin
from app.ecosystem.schemas import (
    BulkDecideRequest,
    CatalogEntityResponse,
    ConfirmResolutionRequest,
    LifecycleTransitionRequest,
    LifecycleTransitionResponse,
    MappingResponse,
    ResolutionCandidateResponse,
    ResolveConflictRequest,
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


@router.get("/compare", response_model=DataResponse[list])
async def compare_entities(
    kind: str = Query(...),
    ids: str = Query(..., description="Comma-separated entity ids (2-6)"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Side-by-side entity comparison: facts, pricing, availability, benchmarks."""
    entity_ids = [x.strip() for x in ids.split(",") if x.strip()]
    return {"data": await CatalogService(db).compare_entities(kind, entity_ids)}


@router.get("/catalog/{segment}/duplicates", response_model=DataResponse[list])
async def catalog_duplicates(
    segment: str,
    threshold: float = Query(0.55, ge=0.3, le=1.0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """Suspected duplicate entity pairs (trigram similarity) — suggestion only."""
    return {
        "data": await CatalogService(db).find_duplicates(
            _kind(segment), threshold=threshold, limit=limit
        )
    }


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
    updates = body.model_dump(exclude_unset=True)
    entity = await CatalogService(db).update(_kind(segment), entity_id, updates)
    await eco_audit(
        db, _user, action="eco.entity_updated", target_type=f"eco_{_kind(segment)}",
        target_id=entity_id, after={k: str(v)[:200] for k, v in updates.items()},
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
    kind = _kind(segment)
    outcome = await CatalogService(db).merge_entities(
        kind, entity_id, target_id, actor_id=user.id
    )
    await eco_audit(
        db, user, action="eco.entity_merged", target_type=f"eco_{kind}",
        target_id=entity_id, after=outcome,
    )
    await db.commit()
    return {"data": outcome}


@router.get("/catalog/{segment}/{entity_id}/scorecard", response_model=DataResponse[dict])
async def entity_scorecard(
    segment: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Backstage-style scorecard: transparent pass/warn/fail checks + evidence."""
    kind = _kind(segment)
    return {"data": await CatalogService(db).scorecard(kind, entity_id)}


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
    kind = _kind(segment)
    before_entity = await CatalogService(db).get(kind, entity_id)
    from_status = before_entity.lifecycle_status
    entity = await LifecycleService(db).transition(
        kind,
        entity_id,
        to_status=body.to_status,
        reason=body.reason,
        note=body.note,
        actor_id=user.id,
    )
    await eco_audit(
        db, user, action="eco.lifecycle_transitioned", target_type=f"eco_{kind}",
        target_id=entity_id, before={"status": from_status},
        after={"status": body.to_status}, reason=body.reason,
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
            str(item["name"])
            .replace("\\", "\\\\")
            .replace(",", "\\,")
            .replace(";", "\\;")
            # RFC 5545: literal newlines MUST be escaped — an unescaped one
            # folds the line and lets a hostile entity name inject arbitrary
            # ICS properties into the event
            .replace("\r", "")
            .replace("\n", "\\n")
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


@router.post(
    "/catalog/{segment}/{entity_id}/resolve-conflict",
    response_model=DataResponse[dict],
)
async def resolve_conflict(
    segment: str,
    entity_id: str,
    body: ResolveConflictRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """§14 curation loop: arbitrate a source conflict per field — a curated
    overlay with full provenance; the disagreeing observations stay visible."""
    kind = _kind(segment)
    decision = await CatalogService(db).resolve_conflict(
        kind,
        entity_id,
        field=body.field,
        chosen_value=body.chosen_value,
        winning_source_id=body.winning_source_id,
        actor_id=user.id,
    )
    await eco_audit(
        db, user, action="eco.conflict_resolved", target_type=f"eco_{kind}",
        target_id=entity_id, after={"field": body.field, "decision": decision},
    )
    await db.commit()
    return {"data": decision}


@router.get(
    "/catalog/{segment}/{entity_id}/corroboration", response_model=DataResponse[dict]
)
async def entity_corroboration(
    segment: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """§14: trust-weighted multi-source corroboration score."""
    return {"data": await CatalogService(db).corroboration(_kind(segment), entity_id)}


@router.get("/search", response_model=DataResponse[list])
async def global_search(
    q: str = Query(..., min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """§14: one search box across all seven catalog kinds (indexed trigram)."""
    return {"data": await CatalogService(db).global_search(q)}


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
    totals: dict = {}
    truncated = False
    for segment, kind in _KIND_SEGMENTS.items():
        # R168: the export IS the integration currency — a silent per-kind
        # cap would hand downstream consumers an incomplete catalog. Page
        # through everything and stamp totals so drift is detectable.
        rows_all = []
        offset = 0
        while True:
            rows, total = await svc.list_entities(kind, limit=500, offset=offset)
            rows_all.extend(rows)
            offset += len(rows)
            if offset >= total or not rows or offset >= 10_000:
                if offset < total:
                    truncated = True  # 10k hard ceiling — flagged, never silent
                break
        totals[segment] = total
        entities[segment] = [
            CatalogEntityResponse.model_validate(r).model_dump(mode="json") for r in rows_all
        ]
    # R169: same completeness rule for mappings — flagged ceiling, not a
    # silent first-2000 slice
    mapping_rows = list(await db.scalars(select(CapabilityMapping).limit(10_001)))
    if len(mapping_rows) > 10_000:
        truncated = True
        mapping_rows = mapping_rows[:10_000]
    mappings = [
        MappingResponse.model_validate(m).model_dump(mode="json") for m in mapping_rows
    ]
    price_rows = list(
        await db.scalars(
            select(PriceObservation)
            .where(PriceObservation.reconciliation_status == "approved")
            .limit(10_001)
        )
    )
    if len(price_rows) > 10_000:
        truncated = True
        price_rows = price_rows[:10_000]
    prices = [
        {
            "entity_kind": p.entity_kind,
            "entity_id": p.entity_id,
            "unit": p.unit,
            "price": float(p.price),
            "currency": p.currency,
            "region": p.region,
        }
        for p in price_rows
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
            "entity_totals": totals,
            "truncated": truncated,
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


@router.post(
    "/resolution-candidates/{candidate_id}/llm-suggest",
    response_model=DataResponse[ResolutionCandidateResponse],
)
async def llm_suggest_resolution(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """§14: LLM tie-breaker for an ambiguous pending candidate. The suggestion
    updates the candidate (method=llm_suggested, confidence <= 0.7) but NEVER
    auto-merges — llm_suggested is excluded from the auto-merge policy."""
    from app.ecosystem.models.catalog import ResolutionCandidate
    from app.ecosystem.services.llm_extraction import suggest_resolution

    candidate = await db.get(ResolutionCandidate, candidate_id)
    if candidate is None:
        raise AppError("NOT_FOUND", "Resolution candidate not found", 404)
    if candidate.status != "pending":
        raise AppError("ECO_INVALID_TRANSITION", "Candidate already decided", 409)
    svc = CatalogService(db)
    similar = await svc.global_search(
        str((candidate.proposed_payload or {}).get("name", "")), limit_per_kind=5
    )
    options = [
        {"id": r["id"], "name": r["canonical_name"], "kind": r["kind"]}
        for r in similar
        if r["kind"] == candidate.entity_kind
    ][:8]
    suggestion = await suggest_resolution(candidate.proposed_payload or {}, options)
    if suggestion and suggestion.get("candidate_id"):
        candidate.candidate_entity_id = suggestion["candidate_id"]
        candidate.match_method = "llm_suggested"
        candidate.confidence = suggestion["confidence"]
    await db.commit()
    return {"data": candidate}


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
    # R176: bulk resolution decisions are irreversible HITL actions — audited
    # like every other admin decision (single confirms audit via merge path)
    await eco_audit(
        db, user, action="eco.resolutions_bulk_decided",
        target_type="eco_resolution_candidate",
        target_id=decided[0]["id"] if decided else "none",
        after={"decision": body.decision, "decided_count": len(decided),
               "failed_count": len(failed)},
    )
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
