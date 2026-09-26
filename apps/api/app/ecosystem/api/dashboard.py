"""Operator workspace + approved-signal endpoints (Parts N, O, P)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import get_feed_user, get_scrape_admin, require_platform_admin
from app.ecosystem.models.observation import CHANGE_SEVERITIES
from app.ecosystem.schemas import ChangeEventResponse
from app.ecosystem.services.dashboard import DashboardService
from app.ecosystem.services.signals import SignalsService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem", tags=["Ecosystem — Dashboard & Signals"])




def _self_url(request) -> str:
    """Feed self-URL without the credential query param."""
    url = request.url.remove_query_params("token")
    return str(url)


def _etag_matches(header: str | None, etag: str) -> bool:
    """RFC 7232 §3.2: If-None-Match may carry a comma-separated validator
    list (proxies and some readers merge them) or `*`. Weak prefixes compare
    equal for GET (weak comparison is allowed for 304s)."""
    if not header:
        return False
    if header.strip() == "*":
        return True
    return any(
        candidate.strip().removeprefix("W/") == etag
        for candidate in header.split(",")
    )


def _check_severity(value: str | None, allowed: frozenset[str]) -> None:
    """R231: filter params must reject unknown severities — a typo
    (?severity=critcal) silently returned an empty feed, reading as
    "no critical changes" to the subscriber."""
    if value is not None and value not in allowed:
        from app.exceptions import AppError

        raise AppError(
            "VALIDATION_ERROR",
            f"Unknown severity {value!r}; allowed: {', '.join(sorted(allowed))}",
            422,
        )


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
    _check_severity(severity, CHANGE_SEVERITIES)
    return {
        "data": await DashboardService(db).change_feed(
            severity=severity, limit=limit, offset=offset
        )
    }


@router.get("/ops/metrics", include_in_schema=True)
async def ops_metrics(
    db: AsyncSession = Depends(get_db),
    # R247: scrapeable by Prometheus via a long-lived admin feed token
    # (?token=) — Bearer admin sessions still work for humans
    _user: User = Depends(get_scrape_admin),
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
    # R264: a dead-lettered eco message is a PROMISED AUTOMATION that
    # silently stopped (§90 class) — it must be a metric, not just a row
    # on the failed-outbox admin endpoint
    outbox_failed = (
        await db.scalar(
            select(func.count())
            .select_from(OutboxMessage)
            .where(OutboxMessage.status == "failed", OutboxMessage.topic.like("eco.%"))
        )
    ) or 0
    lines: list[str] = []

    def emit(name: str, value) -> None:
        # Exposition-format compliance: each metric carries its OWN TYPE line
        # (a TYPE for a name that never appears leaves every real metric
        # untyped in Prometheus)
        if isinstance(value, (int, float)):
            lines.append(f"# TYPE eco_{name} gauge")
            lines.append(f"eco_{name} {value}")

    for key, value in overview.items():
        if isinstance(value, dict):
            for sub, subvalue in value.items():
                emit(f"{key}_{sub}", subvalue)
        else:
            emit(key, value)
    emit("outbox_pending", outbox_pending)
    emit("outbox_failed", outbox_failed)
    return PlainTextResponse(
        "\n".join(lines) + "\n",
        media_type="text/plain; version=0.0.4",
        # R271: admin data reachable via a query token — never shared-cacheable
        headers={"Cache-Control": "private, max-age=0, must-revalidate"},
    )


@router.get("/export/feed-token", response_model=dict)
async def mint_feed_token(
    user: User = Depends(get_current_user),
):
    """R232: exchange a normal session for a narrow-scope feed token to
    embed in Atom URLs (feed readers cannot send Bearer headers)."""
    from app.core.security import create_feed_token

    return {"data": {"token": create_feed_token(user.id), "expires_in_days": 365}}


@router.get("/export/changes.atom", include_in_schema=True)
async def export_changes_atom(
    request: Request = None,
    severity: str | None = None,
    entity_id: Annotated[str | None, Query(min_length=26, max_length=26)] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_feed_user),
):
    """Atom 1.0 feed of typed change events — newest first, XML-escaped
    (change data is untrusted external content, never emitted raw).
    `entity_id` narrows to one canonical entity (GitHub releases.atom
    posture: subscribe to the model you depend on, not the firehose)."""
    import re
    from datetime import UTC, datetime
    from hashlib import sha256
    from xml.sax.saxutils import escape

    from fastapi.responses import Response

    # R230: saxutils.escape only handles <>& — control chars (legal in
    # Postgres text/JSONB, e.g. \x08 from scraped/LLM-extracted values)
    # are ILLEGAL in XML 1.0 and make the whole feed unparseable for every
    # consumer. One poisoned observation must not DoS the subscription
    # surface: strip them before escaping.
    _xml_illegal = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

    def _xml_text(value: str) -> str:
        return escape(_xml_illegal.sub("", value))

    _check_severity(severity, CHANGE_SEVERITIES)
    rows = await DashboardService(db).change_feed(
        severity=severity, canonical_entity_id=entity_id, limit=limit, offset=0
    )
    # R246: a merge re-points every change to the survivor, which would turn
    # long-lived subscription URLs (?entity_id=<duplicate>) into permanently
    # empty feeds. When the filtered feed is empty AND a supersedes edge
    # exists, redirect the reader to the survivor's feed (302 — readers
    # follow redirects; the token and filters ride along).
    if entity_id and not rows and request is not None:
        from sqlalchemy import select

        from app.ecosystem.models.replacement import ReplacementEdge

        successor = await db.scalar(
            select(ReplacementEdge.to_id)
            .where(
                ReplacementEdge.from_id == entity_id,
                ReplacementEdge.edge_type == "supersedes",
            )
            .order_by(ReplacementEdge.created_at.desc())
            .limit(1)
        )
        if successor:
            # replace ONLY the query-param value — a bare str.replace could
            # corrupt a token that happens to contain the 26-char id
            location = str(request.url).replace(
                f"entity_id={entity_id}", f"entity_id={successor}"
            )
            return Response(
                status_code=302,
                headers={"Location": location, "Cache-Control": "private, max-age=0"},
            )

    # R235: feed readers poll on a schedule — honor conditional GET. The
    # change stream is insert-only (retention trims oldest), so the window
    # is identified by (newest id, oldest id, row count) + the filters.
    window = f"{severity}:{entity_id}:{limit}:" + (
        f"{rows[0].id}:{rows[-1].id}:{len(rows)}" if rows else "empty"
    )
    etag = f'"{sha256(window.encode()).hexdigest()[:32]}"'
    # R245: Last-Modified rides along for legacy pollers that only send
    # If-Modified-Since (still common in cron/curl feed scripts). RFC 7232:
    # when If-None-Match is present it takes precedence and IMS is ignored.
    from email.utils import format_datetime, parsedate_to_datetime

    last_modified = (
        format_datetime(rows[0].detected_at, usegmt=True)
        if rows and rows[0].detected_at
        else None
    )
    # R271: query-token requests carry no Authorization header, so shared
    # caches (CDN, corporate proxies) would happily store and replay these
    # responses to OTHER clients. Cache-Control: private confines caching to
    # the requesting client while keeping the ETag revalidation contract.
    cond_headers = {"ETag": etag, "Cache-Control": "private, max-age=0, must-revalidate"}
    if last_modified:
        cond_headers["Last-Modified"] = last_modified
    if request is not None:
        inm = request.headers.get("if-none-match")
        if inm is not None:
            if _etag_matches(inm, etag):
                return Response(status_code=304, headers=cond_headers)
        else:
            ims = request.headers.get("if-modified-since")
            if ims and last_modified:
                try:
                    ims_dt = parsedate_to_datetime(ims)
                    latest = rows[0].detected_at
                    if int(latest.timestamp()) <= int(ims_dt.timestamp()):
                        return Response(status_code=304, headers=cond_headers)
                except (TypeError, ValueError):
                    pass  # malformed date: serve the full response

    entries = []
    updated = None
    for c in rows:
        detected = c.detected_at.isoformat() if c.detected_at else ""
        updated = updated or detected
        title = _xml_text(f"[{c.severity}] {c.change_type} · {c.field}")
        summary = _xml_text(
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
        "<author><name>OpenSkill Studio</name></author>"
        # R252: rel=self is the validator-recommended feed identity; the
        # token is stripped so the credential never round-trips in the body
        + (
            f'<link rel="self" href="{_xml_text(_self_url(request))}"/>'
            if request is not None
            else ""
        )
        + f"<updated>{updated or datetime.now(UTC).isoformat()}</updated>"
        + "".join(entries)
        + "</feed>"
    )
    return Response(
        content=xml, media_type="application/atom+xml", headers=cond_headers
    )


@router.get("/export/changes", response_model=dict)
async def export_changes_delta(
    since: str = Query(..., description="ISO-8601 timestamp"),
    since_id: Annotated[str | None, Query(min_length=26, max_length=26)] = None,
    limit: int = Query(200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """§17 (deps.dev delta posture): consumers of the catalog export poll this
    delta feed instead of re-downloading the world — typed change events since
    a (timestamp, id) cursor, oldest first.

    R194: a bare `detected_at > since` cursor silently DROPS rows sharing the
    boundary timestamp (batch inserts share server_default now()). The cursor
    is lexicographic on (detected_at, id): pass back BOTH next_since and
    next_since_id. Timestamp-only callers keep working (strictly-greater
    semantics, unchanged) — they just shouldn't batch at page boundaries.
    """
    from datetime import datetime

    from sqlalchemy import or_, select

    from app.ecosystem.models.observation import ChangeEvent
    from app.ecosystem.schemas import ChangeEventResponse
    from app.exceptions import AppError

    try:
        since_ts = datetime.fromisoformat(since.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AppError("VALIDATION_ERROR", "since must be ISO-8601", 422) from exc
    if since_id:
        cursor_where = or_(
            ChangeEvent.detected_at > since_ts,
            (ChangeEvent.detected_at == since_ts) & (ChangeEvent.id > since_id),
        )
    else:
        cursor_where = ChangeEvent.detected_at > since_ts
    rows = list(
        await db.scalars(
            select(ChangeEvent)
            .where(cursor_where)
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
            "next_since_id": rows[-1].id if rows else since_id,
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
