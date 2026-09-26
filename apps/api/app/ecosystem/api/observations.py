"""Observation ledger + change feed endpoints (ADR-016 Part B)."""

import hashlib
import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import eco_audit, require_platform_admin
from app.ecosystem.models.observation import (
    OBSERVATION_EVENT_TYPES,
    ChangeEvent,
    EcosystemObservation,
)
from app.ecosystem.schemas import (
    BulkIdsRequest,
    ChangeEventResponse,
    LLMExtractRequest,
    ManualObservationRequest,
    ObservationResponse,
)
from app.ecosystem.security import sanitize_text
from app.ecosystem.services.change_detection import detect_changes
from app.ecosystem.services.resolution import propose_resolution
from app.ecosystem.services.sources import SourceService
from app.exceptions import AppError
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem", tags=["Ecosystem — Observations"])


@router.get("/observations", response_model=dict)
async def list_observations(
    source_id: str | None = None,
    event_type: str | None = None,
    entity_kind: str | None = None,
    canonical_entity_id: str | None = None,
    human_verified: bool | None = None,
    injection_flagged: bool | None = Query(
        None, description="ADR-016 §11.2: heuristic flags filter — advisory, never blocking"
    ),
    cursor: str | None = Query(
        None, description="ULID cursor (id of last item from the previous page)"
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0, description="Legacy; prefer cursor"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Append-only feed → ULID cursor pagination (§13): stable under concurrent
    inserts, unlike offset pages which shift as new observations land."""
    query = select(EcosystemObservation)
    if source_id:
        query = query.where(EcosystemObservation.source_id == source_id)
    if injection_flagged is not None:
        flag = EcosystemObservation.normalized["injection_flag"].as_boolean()
        query = query.where(flag.is_(True) if injection_flagged else flag.isnot(True))
    if event_type:
        query = query.where(EcosystemObservation.event_type == event_type)
    if entity_kind:
        query = query.where(EcosystemObservation.entity_kind == entity_kind)
    if canonical_entity_id:
        query = query.where(EcosystemObservation.canonical_entity_id == canonical_entity_id)
    if human_verified is not None:
        query = query.where(EcosystemObservation.human_verified == human_verified)
    if cursor:
        query = query.where(EcosystemObservation.id < cursor)
        query = query.order_by(EcosystemObservation.id.desc()).limit(limit + 1)
    else:
        query = (
            query.order_by(EcosystemObservation.id.desc()).limit(limit + 1).offset(offset)
        )
    rows = list(await db.scalars(query))
    has_more = len(rows) > limit
    rows = rows[:limit]
    return {
        "data": [ObservationResponse.model_validate(r).model_dump() for r in rows],
        "meta": {
            "has_more": has_more,
            "next_cursor": rows[-1].id if has_more and rows else None,
        },
    }


@router.post("/observations", response_model=DataResponse[ObservationResponse], status_code=201)
async def create_manual_observation(
    body: ManualObservationRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """Manual analyst input — only against a manual_analyst/internal source."""
    source = await SourceService(db).get(body.source_id)
    if source.source_type not in ("manual_analyst", "internal_research"):
        raise AppError(
            "VALIDATION_ERROR",
            "Manual observations require a manual_analyst or internal_research source",
            422,
        )
    # R102: manual input is still untrusted-adjacent — the analyst pastes
    # from external pages. Validate the enum, screen the ref, refuse
    # non-http(s) provenance (rendered as a link on Discoveries), and bound
    # the normalized payload like every adapter path.
    if body.event_type not in OBSERVATION_EVENT_TYPES:
        raise AppError("VALIDATION_ERROR", f"Unknown event type: {body.event_type}", 422)
    provenance = body.provenance_url
    if provenance and not provenance.lower().startswith(("http://", "https://")):
        raise AppError("VALIDATION_ERROR", "provenance_url must be http(s)", 422)
    raw = json.dumps(body.normalized, sort_keys=True, default=str).encode()
    if len(raw) > 100_000:
        raise AppError("VALIDATION_ERROR", "normalized payload too large (100k max)", 422)
    obs = EcosystemObservation(
        source_id=source.id,
        event_type=body.event_type,
        entity_kind=body.entity_kind,
        external_ref=sanitize_text(body.external_ref, 500),
        raw_hash=hashlib.sha256(raw).hexdigest(),
        normalized=body.normalized,
        parser_version=source.parser_version,
        confidence=0.9,
        provenance_url=provenance,
        extraction_method="manual",
    )
    db.add(obs)
    await db.flush()
    await detect_changes(db, obs)
    await propose_resolution(db, obs, trust_level=source.trust_level)
    await eco_audit(
        db, _user, action="eco.observation_manual_created",
        target_type="eco_observation", target_id=obs.id,
        after={"event_type": obs.event_type, "source_id": source.id},
    )
    await db.commit()
    return {"data": obs}


@router.post("/observations/bulk-verify", response_model=DataResponse[dict])
async def bulk_verify_observations(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """ADR-016 §11.1 — drain the review queue cheaply. Idempotent; missing ids
    are reported, never fatal."""
    verified: list[str] = []
    missing: list[str] = []
    now = datetime.now(UTC)
    for obs_id in body.ids:
        obs = await db.get(EcosystemObservation, obs_id)
        if obs is None:
            missing.append(obs_id)
            continue
        if not obs.human_verified:
            obs.human_verified = True
            obs.verified_by = user.id
            obs.verified_at = now
        verified.append(obs_id)
    await eco_audit(
        db, user, action="eco.observations_bulk_verified",
        target_type="eco_observation", target_id=verified[0] if verified else "none",
        after={"verified_count": len(verified), "missing_count": len(missing)},
    )
    await db.commit()
    return {"data": {"verified": verified, "missing": missing}}


@router.post(
    "/observations/extract-llm",
    response_model=DataResponse[list[ObservationResponse]],
    status_code=201,
)
async def extract_observations_llm(
    body: LLMExtractRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """§14 (Snyk AI+HITL): extract model facts from untrusted free text via the
    platform LLM. Every resulting observation is extraction_method='llm',
    confidence-capped, unverified — the human review queue is the gate before
    any downstream automation sees it."""
    from app.ecosystem.services.llm_extraction import LLM_CONFIDENCE_CAP, extract_model_facts

    source = await SourceService(db).get(body.source_id)
    if source.source_type not in ("manual_analyst", "internal_research"):
        raise AppError(
            "VALIDATION_ERROR",
            "LLM extraction requires a manual_analyst or internal_research source",
            422,
        )
    facts = await extract_model_facts(body.text)
    created: list[EcosystemObservation] = []
    for fact in facts:
        raw = json.dumps(fact, sort_keys=True, default=str).encode()
        obs = EcosystemObservation(
            source_id=source.id,
            event_type="model_released",
            entity_kind="model_version" if fact.get("version") else body.entity_kind,
            external_ref=fact.get("official_id") or fact.get("name"),
            raw_hash=hashlib.sha256(raw).hexdigest(),
            normalized=fact,
            parser_version="llm-1.0",
            confidence=min(0.6, LLM_CONFIDENCE_CAP),
            extraction_method="llm",
        )
        db.add(obs)
        try:
            await db.flush()
        except Exception:  # noqa: BLE001 — duplicate raw_hash → idempotent skip
            await db.rollback()
            continue
        await detect_changes(db, obs)
        await propose_resolution(db, obs, trust_level=source.trust_level)
        created.append(obs)
    await db.commit()
    return {"data": created}


@router.get("/observations/{obs_id}", response_model=DataResponse[ObservationResponse])
async def get_observation(
    obs_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    obs = await db.get(EcosystemObservation, obs_id)
    if not obs:
        raise AppError("NOT_FOUND", "Observation not found", 404)
    return {"data": obs}


@router.post("/observations/{obs_id}/verify", response_model=DataResponse[ObservationResponse])
async def verify_observation(
    obs_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    obs = await db.get(EcosystemObservation, obs_id)
    if not obs:
        raise AppError("NOT_FOUND", "Observation not found", 404)
    obs.human_verified = True
    obs.verified_by = user.id
    obs.verified_at = datetime.now(UTC)
    await db.commit()
    return {"data": obs}


@router.get("/changes", response_model=dict)
async def list_changes(
    change_type: str | None = None,
    severity: str | None = None,
    acknowledged: bool | None = None,
    canonical_entity_id: str | None = None,
    cursor: str | None = Query(None, description="ULID cursor (id of last item)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0, description="Legacy; prefer cursor"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    from app.ecosystem.api.dashboard import _check_severity
    from app.ecosystem.models.observation import CHANGE_SEVERITIES

    _check_severity(severity, CHANGE_SEVERITIES)
    query = select(ChangeEvent)
    if change_type:
        query = query.where(ChangeEvent.change_type == change_type)
    if severity:
        query = query.where(ChangeEvent.severity == severity)
    if acknowledged is not None:
        query = query.where(ChangeEvent.acknowledged == acknowledged)
    if canonical_entity_id:
        query = query.where(ChangeEvent.canonical_entity_id == canonical_entity_id)
    if cursor:
        query = query.where(ChangeEvent.id < cursor)
        query = query.order_by(ChangeEvent.id.desc()).limit(limit + 1)
    else:
        query = query.order_by(ChangeEvent.id.desc()).limit(limit + 1).offset(offset)
    rows = list(await db.scalars(query))
    has_more = len(rows) > limit
    rows = rows[:limit]
    return {
        "data": [ChangeEventResponse.model_validate(r).model_dump() for r in rows],
        "meta": {
            "has_more": has_more,
            "next_cursor": rows[-1].id if has_more and rows else None,
        },
    }


@router.post("/changes/bulk-acknowledge", response_model=DataResponse[dict])
async def bulk_acknowledge_changes(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """ADR-016 §11.1 — drain the triage queue like bulk-verify: idempotent,
    missing ids reported, never fatal."""
    acknowledged: list[str] = []
    missing: list[str] = []
    for change_id in body.ids:
        change = await db.get(ChangeEvent, change_id)
        if change is None:
            missing.append(change_id)
            continue
        if not change.acknowledged:
            change.acknowledged = True
            change.acknowledged_by = user.id
        acknowledged.append(change_id)
    await eco_audit(
        db, user, action="eco.changes_bulk_acknowledged",
        target_type="eco_change_event",
        target_id=acknowledged[0] if acknowledged else "none",
        after={"acknowledged_count": len(acknowledged), "missing_count": len(missing)},
    )
    await db.commit()
    return {"data": {"acknowledged": acknowledged, "missing": missing}}


@router.post("/changes/{change_id}/acknowledge", response_model=DataResponse[ChangeEventResponse])
async def acknowledge_change(
    change_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    change = await db.get(ChangeEvent, change_id)
    if not change:
        raise AppError("NOT_FOUND", "Change event not found", 404)
    change.acknowledged = True
    change.acknowledged_by = user.id
    await db.commit()
    return {"data": change}
