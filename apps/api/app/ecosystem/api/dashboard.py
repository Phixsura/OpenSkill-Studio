"""Operator workspace + approved-signal endpoints (Parts N, O, P)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import require_platform_admin
from app.ecosystem.schemas import ChangeEventResponse
from app.ecosystem.services.dashboard import DashboardService
from app.ecosystem.services.signals import SignalsService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem", tags=["Ecosystem — Dashboard & Signals"])


@router.get("/dashboard", response_model=DataResponse[dict])
async def dashboard_overview(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await DashboardService(db).overview()}


@router.get("/dashboard/trending", response_model=DataResponse[list])
async def trending_entities(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Entities ranked by observation velocity (evidence counting only)."""
    return {"data": await DashboardService(db).trending(days=days, limit=limit)}


@router.get("/dashboard/coverage", response_model=DataResponse[dict])
async def catalog_coverage(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Per-kind catalog completeness (capability/benchmark/pricing coverage)."""
    return {"data": await DashboardService(db).coverage()}


@router.get("/dashboard/change-feed", response_model=DataResponse[list[ChangeEventResponse]])
async def change_feed(
    severity: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {
        "data": await DashboardService(db).change_feed(
            severity=severity, limit=limit, offset=offset
        )
    }


@router.get("/ops/metrics", include_in_schema=True)
async def ops_metrics(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """§17 (Datadog/Prometheus posture): the subsystem exposes its own health
    as scrape-able plaintext metrics — queue depths, review debt, staleness."""
    from fastapi.responses import PlainTextResponse
    from sqlalchemy import func, select

    from app.controlplane.models.outbox import OutboxMessage

    overview = await DashboardService(db).overview()
    outbox_pending = (
        await db.scalar(
            select(func.count())
            .select_from(OutboxMessage)
            .where(OutboxMessage.status == "pending", OutboxMessage.topic.like("eco.%"))
        )
    ) or 0
    lines = ["# TYPE eco_gauge gauge"]

    def emit(name: str, value) -> None:
        if isinstance(value, (int, float)):
            lines.append(f"eco_{name} {value}")

    for key, value in overview.items():
        if isinstance(value, dict):
            for sub, subvalue in value.items():
                emit(f"{key}_{sub}", subvalue)
        else:
            emit(key, value)
    emit("outbox_pending", outbox_pending)
    return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")


@router.get("/export/changes.atom", include_in_schema=True)
async def export_changes_atom(
    severity: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Atom 1.0 feed of typed change events — newest first, XML-escaped
    (change data is untrusted external content, never emitted raw)."""
    from xml.sax.saxutils import escape

    from fastapi.responses import Response

    rows = await DashboardService(db).change_feed(severity=severity, limit=limit, offset=0)
    entries = []
    updated = None
    for c in rows:
        detected = c.detected_at.isoformat() if c.detected_at else ""
        updated = updated or detected
        title = escape(f"[{c.severity}] {c.change_type} · {c.field}")
        summary = escape(
            f"entity_kind={c.entity_kind or '?'} old={c.old_value} new={c.new_value}"
        )
        entries.append(
            f"<entry><id>urn:openskill:eco-change:{c.id}</id>"
            f"<title>{title}</title><updated>{detected}</updated>"
            f"<summary>{summary}</summary></entry>"
        )
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        "<id>urn:openskill:eco-changes</id>"
        "<title>OpenSkill Ecosystem Change Feed</title>"
        f"<updated>{updated or ''}</updated>" + "".join(entries) + "</feed>"
    )
    return Response(content=xml, media_type="application/atom+xml")


@router.get("/export/changes", response_model=dict)
async def export_changes_delta(
    since: str = Query(..., description="ISO-8601 timestamp"),
    limit: int = Query(200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """§17 (deps.dev delta posture): consumers of the catalog export poll this
    delta feed instead of re-downloading the world — typed change events since
    a timestamp, oldest first, cursor by last detected_at."""
    from datetime import datetime

    from sqlalchemy import select

    from app.ecosystem.models.observation import ChangeEvent
    from app.ecosystem.schemas import ChangeEventResponse
    from app.exceptions import AppError

    try:
        since_ts = datetime.fromisoformat(since.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AppError("VALIDATION_ERROR", "since must be ISO-8601", 422) from exc
    rows = list(
        await db.scalars(
            select(ChangeEvent)
            .where(ChangeEvent.detected_at > since_ts)
            .order_by(ChangeEvent.detected_at.asc(), ChangeEvent.id.asc())
            .limit(limit + 1)
        )
    )
    has_more = len(rows) > limit
    rows = rows[:limit]
    return {
        "data": [ChangeEventResponse.model_validate(r).model_dump() for r in rows],
        "meta": {
            "has_more": has_more,
            "next_since": rows[-1].detected_at.isoformat() if rows else since,
        },
    }


@router.get("/audit", response_model=dict)
async def eco_audit_trail(
    action: str | None = Query(None, max_length=60),
    target_id: str | None = Query(None, max_length=26),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """§17: the eco slice of the immutable commercial audit trail, queryable
    in-product (enterprise governance baseline)."""
    from sqlalchemy import select

    from app.controlplane.models.audit import CommercialAuditEvent

    query = select(CommercialAuditEvent).where(
        CommercialAuditEvent.action.like("eco.%")
    )
    if action:
        query = query.where(CommercialAuditEvent.action == action)
    if target_id:
        query = query.where(CommercialAuditEvent.target_id == target_id)
    rows = list(
        await db.scalars(query.order_by(CommercialAuditEvent.id.desc()).limit(limit))
    )
    return {
        "data": [
            {
                "id": e.id,
                "actor_user_id": e.actor_user_id,
                "action": e.action,
                "target_type": e.target_type,
                "target_id": e.target_id,
                "before": e.before,
                "after": e.after,
                "reason": e.reason,
            }
            for e in rows
        ]
    }


@router.get("/audit.csv", include_in_schema=True)
async def eco_audit_trail_csv(
    action: str | None = Query(None, max_length=60),
    target_id: str | None = Query(None, max_length=26),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    """§17 compliance export: the eco audit slice as CSV. Values are
    csv-module quoted (untrusted content never breaks the format) and
    cells starting with =,+,-,@ are prefixed to defuse spreadsheet
    formula injection."""
    import csv
    import io
    import json as _json

    from fastapi.responses import Response
    from sqlalchemy import select

    from app.controlplane.models.audit import CommercialAuditEvent

    query = select(CommercialAuditEvent).where(
        CommercialAuditEvent.action.like("eco.%")
    )
    if action:
        query = query.where(CommercialAuditEvent.action == action)
    if target_id:
        query = query.where(CommercialAuditEvent.target_id == target_id)
    rows = list(
        await db.scalars(query.order_by(CommercialAuditEvent.id.desc()).limit(limit))
    )

    def _cell(value) -> str:
        text = _json.dumps(value, default=str) if isinstance(value, (dict, list)) else str(value or "")
        return f"'{text}" if text[:1] in ("=", "+", "-", "@") else text

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["id", "actor_user_id", "action", "target_type", "target_id", "before", "after", "reason"]
    )
    for e in rows:
        writer.writerow([
            _cell(e.id), _cell(e.actor_user_id), _cell(e.action), _cell(e.target_type),
            _cell(e.target_id), _cell(e.before), _cell(e.after), _cell(e.reason),
        ])
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=eco-audit.csv"},
    )


@router.get("/signals/matching", response_model=DataResponse[list])
async def matching_signals(
    capability_key: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Approved-only intelligence signals (Part N). Raw observations never leak."""
    return {"data": await SignalsService(db).matching_signals(capability_key=capability_key)}


@router.get("/signals/workforce", response_model=DataResponse[list])
async def workforce_signals(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Emerging/obsolete capability planning signals (Part O). Advisory only."""
    return {"data": await SignalsService(db).workforce_signals()}


@router.get("/registry-badges", response_model=DataResponse[dict])
async def registry_badges(
    refs: str = Query(..., description="Comma-separated kind:id pairs"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    entity_refs = []
    for pair in refs.split(",")[:50]:
        if ":" in pair:
            kind, _, entity_id = pair.strip().partition(":")
            entity_refs.append((kind, entity_id))
    return {"data": await SignalsService(db).registry_badges(entity_refs=entity_refs)}
