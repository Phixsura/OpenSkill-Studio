"""Observation ledger + change feed endpoints (ADR-016 Part B)."""

import hashlib
import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import require_platform_admin
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.schemas import (
    BulkIdsRequest,
    ChangeEventResponse,
    ManualObservationRequest,
    ObservationResponse,
)
from app.ecosystem.services.change_detection import detect_changes
from app.ecosystem.services.resolution import propose_resolution
from app.ecosystem.services.sources import SourceService
from app.exceptions import AppError
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem", tags=["Ecosystem — Observations"])


@router.get("/observations", response_model=DataResponse[list[ObservationResponse]])
async def list_observations(
    source_id: str | None = None,
    event_type: str | None = None,
    entity_kind: str | None = None,
    canonical_entity_id: str | None = None,
    human_verified: bool | None = None,
    injection_flagged: bool | None = Query(
        None, description="ADR-016 §11.2: heuristic flags filter — advisory, never blocking"
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
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
    rows = await db.scalars(
        query.order_by(EcosystemObservation.observed_at.desc()).limit(limit).offset(offset)
    )
    return {"data": list(rows)}


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
    raw = json.dumps(body.normalized, sort_keys=True, default=str).encode()
    obs = EcosystemObservation(
        source_id=source.id,
        event_type=body.event_type,
        entity_kind=body.entity_kind,
        external_ref=body.external_ref,
        raw_hash=hashlib.sha256(raw).hexdigest(),
        normalized=body.normalized,
        parser_version=source.parser_version,
        confidence=0.9,
        provenance_url=body.provenance_url,
        extraction_method="manual",
    )
    db.add(obs)
    await db.flush()
    await detect_changes(db, obs)
    await propose_resolution(db, obs, trust_level=source.trust_level)
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
    await db.commit()
    return {"data": {"verified": verified, "missing": missing}}


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


@router.get("/changes", response_model=DataResponse[list[ChangeEventResponse]])
async def list_changes(
    change_type: str | None = None,
    severity: str | None = None,
    acknowledged: bool | None = None,
    canonical_entity_id: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    query = select(ChangeEvent)
    if change_type:
        query = query.where(ChangeEvent.change_type == change_type)
    if severity:
        query = query.where(ChangeEvent.severity == severity)
    if acknowledged is not None:
        query = query.where(ChangeEvent.acknowledged == acknowledged)
    if canonical_entity_id:
        query = query.where(ChangeEvent.canonical_entity_id == canonical_entity_id)
    rows = await db.scalars(
        query.order_by(ChangeEvent.detected_at.desc()).limit(limit).offset(offset)
    )
    return {"data": list(rows)}


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
