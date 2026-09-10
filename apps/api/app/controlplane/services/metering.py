"""Usage metering: emit_usage, adjustments, sweeps (ADR-014 §3)."""

import math
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation

import structlog
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.outbox import enqueue
from app.controlplane.models.usage import USAGE_SOURCES, USAGE_TYPES, UsageEvent
from app.controlplane.services.audit import Actor, record_audit
from app.exceptions import AppError

log = structlog.get_logger()

# UsageEvent.quantity is Numeric(18, 6) — 12 integer digits.
MAX_QUANTITY = Decimal("999999999999.999999")


async def emit_usage(
    db: AsyncSession,
    *,
    tenant_id: str,
    org_id: str,
    usage_type: str,
    quantity,
    occurred_at: datetime,
    source: str,
    idempotency_key: str | None = None,
    user_id: str | None = None,
    project_id: str | None = None,
    workflow_run_id: str | None = None,
    evaluation_task_id: str | None = None,
    provider_connection_id: str | None = None,
    provider: str | None = None,
    model_or_service: str | None = None,
    adjustment_of_id: str | None = None,
    metadata: dict | None = None,
) -> UsageEvent | None:
    """Append a usage event + outbox message in the caller's transaction.

    Idempotent: ON CONFLICT (tenant_id, idempotency_key) DO NOTHING → returns
    None on duplicate. Never commits — atomicity with the business write
    belongs to the caller. Negative quantities are legal only for adjustments.
    """
    unit = USAGE_TYPES.get(usage_type)
    if unit is None:
        raise AppError("UNKNOWN_USAGE_TYPE", f"Unknown usage type '{usage_type}'", 422)
    if source not in USAGE_SOURCES:
        raise AppError("VALIDATION_ERROR", f"Unknown usage source '{source}'", 422)
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation as exc:
        raise AppError("INVALID_QUANTITY", "Quantity is not a valid number", 422) from exc
    if not qty.is_finite() or (isinstance(quantity, float) and not math.isfinite(quantity)):
        raise AppError("INVALID_QUANTITY", "Quantity must be finite", 422)
    if qty < 0 and source != "adjustment":
        raise AppError("INVALID_QUANTITY", "Negative quantity requires an adjustment", 422)
    # R325: gate to the true column bound (Numeric(18,6)) — an oversized
    # quantity (≥1e12) overflowed at the INSERT as an asyncpg DataError,
    # which carries no sqlstate for the global backstop (R88 class): a raw
    # 500 on the ingest API, and in the workflow step-usage path it escaped
    # the `except AppError` containment and aborted the run's transaction.
    if qty.copy_abs() > MAX_QUANTITY:
        raise AppError("INVALID_QUANTITY", "Quantity exceeds the maximum recordable value", 422)

    from ulid import ULID

    event_id = str(ULID())
    stmt = (
        pg_insert(UsageEvent)
        .values(
            id=event_id,
            tenant_id=tenant_id,
            org_id=org_id,
            user_id=user_id,
            project_id=project_id,
            workflow_run_id=workflow_run_id,
            evaluation_task_id=evaluation_task_id,
            provider_connection_id=provider_connection_id,
            provider=provider,
            model_or_service=model_or_service,
            usage_type=usage_type,
            quantity=qty,
            unit=unit,
            occurred_at=occurred_at,
            idempotency_key=idempotency_key,
            source=source,
            adjustment_of_id=adjustment_of_id,
            metadata_=metadata or {},
        )
        .on_conflict_do_nothing(
            # R113[M17]: composite target matches uq_cp_usage_idem_tenant —
            # keys are per-tenant; the old (idempotency_key) target let one
            # tenant's key swallow another tenant's billable event.
            index_elements=["tenant_id", "idempotency_key"],
            # Partial unique index (WHERE idempotency_key IS NOT NULL) —
            # Postgres requires the matching predicate for inference.
            index_where=UsageEvent.idempotency_key.isnot(None),
        )
        .returning(UsageEvent.id)
    )
    if idempotency_key is None:
        # No conflict target without a key — plain insert
        event = UsageEvent(
            id=event_id,
            tenant_id=tenant_id,
            org_id=org_id,
            user_id=user_id,
            project_id=project_id,
            workflow_run_id=workflow_run_id,
            evaluation_task_id=evaluation_task_id,
            provider_connection_id=provider_connection_id,
            provider=provider,
            model_or_service=model_or_service,
            usage_type=usage_type,
            quantity=qty,
            unit=unit,
            occurred_at=occurred_at,
            source=source,
            adjustment_of_id=adjustment_of_id,
            metadata_=metadata or {},
        )
        db.add(event)
        await db.flush()
        enqueue(db, "usage.recorded", {"usage_event_id": event.id})
        return event

    inserted = (await db.execute(stmt)).scalar_one_or_none()
    if inserted is None:
        return None  # duplicate — no-op for the caller
    enqueue(db, "usage.recorded", {"usage_event_id": inserted})
    return await db.get(UsageEvent, inserted)


async def ingest_adjustment(
    db: AsyncSession,
    *,
    original_event_id: str,
    delta_quantity,
    reason: str,
    actor: Actor,
    idempotency_key: str | None = None,
) -> UsageEvent:
    """Explicit correction: a new signed event referencing the original.
    There is NO update path for usage history."""
    original = await db.get(UsageEvent, original_event_id)
    if original is None:
        raise AppError("USAGE_EVENT_NOT_FOUND", "Usage event not found", 404)
    # R130[37]: a VOIDED rating means the original was struck from billing
    # entirely (void_rated is the other correction path). Layering a negative
    # adjustment on top double-corrects — the tenant gets a free credit for
    # usage that was never billed. Force ops to pick one path.
    from app.controlplane.models.pricing import RatedUsage

    # R132 ([13]): FOR UPDATE — void_rated's gate reads usage_events while
    # this gate reads rated_usage (disjoint write-sets = classic write skew:
    # a concurrent void + adjust both passed their gates, double-crediting).
    # Locking the rating row serializes the two: void_rated's guarded UPDATE
    # on the same row blocks behind this lock, and its own gate then sees the
    # committed adjustment.
    rating_row = (
        await db.execute(
            select(RatedUsage).where(RatedUsage.usage_event_id == original.id).with_for_update()
        )
    ).scalar_one_or_none()
    if rating_row is not None and rating_row.status == "voided":
        raise AppError(
            "VALIDATION_ERROR",
            "Original event's rating was voided — it was never billed; "
            "an adjustment would double-correct",
            409,
        )
    event = await emit_usage(
        db,
        tenant_id=original.tenant_id,
        org_id=original.org_id,
        usage_type=original.usage_type,
        quantity=delta_quantity,
        occurred_at=original.occurred_at,
        source="adjustment",
        idempotency_key=idempotency_key,
        provider=original.provider,
        model_or_service=original.model_or_service,
        # R101[H16]: carry ALL refs — rating's offering-fallback cost ladder
        # resolves via workflow_run_id, so a reversal without it rated the
        # delta at 0 instead of mirroring the original's cost basis.
        user_id=original.user_id,
        project_id=original.project_id,
        workflow_run_id=original.workflow_run_id,
        evaluation_task_id=original.evaluation_task_id,
        provider_connection_id=original.provider_connection_id,
        adjustment_of_id=original.id,
        metadata={"reason": reason},
    )
    if event is None:
        # R131 ([10]): mirror manual ingest's duplicate semantics — a keyed
        # RETRY returns the original adjustment (idempotent success), instead
        # of a 409 that invites the client to retry with a FRESH key and
        # double-book the correction.
        # R132 ([F6]): scope the lookup to the ORIGINAL's tenant — the unique
        # index is per-tenant (cp16), so an unscoped key query could match
        # another tenant's event and mis-handle a legitimate retry.
        existing = (
            await db.execute(
                select(UsageEvent).where(
                    UsageEvent.idempotency_key == idempotency_key,
                    UsageEvent.tenant_id == original.tenant_id,
                )
            )
        ).scalar_one_or_none()
        if existing is not None and existing.adjustment_of_id == original.id:
            # R132 ([15]): idempotent replay only for the SAME payload — a
            # same-key retry with a different delta silently returned the old
            # adjustment as a fresh 201, swallowing a distinct mutation
            # (Stripe-style key semantics: same key + different payload = 409).
            from decimal import ROUND_HALF_UP, Decimal

            # R133 ([F8]): quantize BOTH sides to the column's 6dp scale — the
            # stored value is Numeric(18,6)-truncated, so a legitimately
            # identical retry with >6dp input compared unequal (false 409).
            # R134 ([F13]): ROUND_HALF_UP — Decimal's default ROUND_HALF_EVEN
            # disagrees with Postgres numeric (round half AWAY from zero) on
            # exact 7th-decimal ties (0.0000005 stored 0.000001, quantized
            # 0.000000 under bankers' rounding → false 409 on identical retry).
            _scale = Decimal("0.000001")
            if Decimal(str(existing.quantity)).quantize(_scale, rounding=ROUND_HALF_UP) != Decimal(
                str(delta_quantity)
            ).quantize(_scale, rounding=ROUND_HALF_UP):
                raise AppError(
                    "VALIDATION_ERROR",
                    "Idempotency key reused with a different delta_quantity",
                    409,
                )
            return existing
        raise AppError("VALIDATION_ERROR", "Duplicate adjustment idempotency key", 409)
    # R130[34]: an adjustment for a tenant with NO open billing period (sub
    # terminally closed / never subscribed) will rate but NEVER be swept into
    # an invoice — no future close exists. The money silently evaporates.
    # Warn loudly so ops route the correction via manual invoice or a credit
    # adjustment instead (the audit row alone gave no signal).
    from app.controlplane.models.billing import BillingPeriod

    has_open = (
        await db.execute(
            select(BillingPeriod.id)
            .where(
                BillingPeriod.tenant_id == original.tenant_id,
                BillingPeriod.status == "open",
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if has_open is None:
        log.warning(
            "cp_adjustment_no_open_period",
            usage_event_id=event.id,
            original_event_id=original.id,
            tenant_id=original.tenant_id,
            detail="no open billing period — this adjustment will never be "
            "invoiced; use a manual invoice or credit adjustment",
        )
    await record_audit(
        db,
        actor=actor,
        action="usage.adjusted",
        target_type="usage_event",
        target_id=original.id,
        tenant_id=original.tenant_id,
        after={"adjustment_event_id": event.id, "delta": str(delta_quantity)},
        reason=reason,
    )
    return event


# ── Sweeps (worker crons + CLI) ──────────────────────────────


async def sweep_storage(
    db: AsyncSession,
    for_date: datetime | None = None,
    org_ids: list[str] | None = None,
) -> int:
    """Daily storage_gb_day events per org. Idempotency: storage:{org}:{date}.

    R257: this used to loop over EVERY non-archived org running two aggregate
    queries each — O(2N) round trips. Past ~10^5 orgs the daily cron blew
    arq's 300s job_timeout, the single commit rolled back wholesale, and the
    next night repeated it: storage billing silently stopped platform-wide.
    Aggregate once with GROUP BY (the sweep_seats pattern) so only orgs that
    actually hold bytes are visited. `org_ids` narrows the sweep for a
    targeted ops re-run (e.g. after fixing a poison org) and for tests.
    """
    from app.models.organization import Organization, OrgStatus
    from app.models.project import ProjectAsset, Submission, SubmissionItem

    day = (for_date or datetime.now(UTC)).date().isoformat()
    totals: dict[str, int] = {}
    item_q = (
        select(Submission.org_id, func.sum(SubmissionItem.file_size))
        .join(Submission, Submission.id == SubmissionItem.submission_id)
        .group_by(Submission.org_id)
    )
    asset_q = select(ProjectAsset.org_id, func.sum(ProjectAsset.file_size)).group_by(
        ProjectAsset.org_id
    )
    if org_ids is not None:
        item_q = item_q.where(Submission.org_id.in_(org_ids))
        asset_q = asset_q.where(ProjectAsset.org_id.in_(org_ids))
    for org_id, nbytes in (await db.execute(item_q)).all():
        totals[org_id] = totals.get(org_id, 0) + int(nbytes or 0)
    for org_id, nbytes in (await db.execute(asset_q)).all():
        totals[org_id] = totals.get(org_id, 0) + int(nbytes or 0)
    totals = {k: v for k, v in totals.items() if v > 0}
    if not totals:
        return 0
    tenant_by_org: dict[str, str] = {}
    ids = list(totals)
    for i in range(0, len(ids), 5000):  # bounded IN-list chunks
        rows = await db.execute(
            select(Organization.id, Organization.tenant_id).where(
                Organization.id.in_(ids[i : i + 5000]),
                Organization.status != OrgStatus.ARCHIVED,
            )
        )
        tenant_by_org.update(dict(rows.all()))
    emitted = 0
    for org_id, total in totals.items():
        tenant_id = tenant_by_org.get(org_id)
        if tenant_id is None:  # archived org — not billed
            continue
        # R169: isolate each org in a SAVEPOINT so one org whose emit raises
        # can't abort the whole DAILY storage sweep (the expire_promotional/
        # R168 per-item pattern). Without it a single poison org rolled back
        # every org's event and the sweep re-failed each day — no storage
        # billed platform-wide until the org was fixed.
        try:
            async with db.begin_nested():
                gb = (Decimal(total) / Decimal(1073741824)).quantize(Decimal("0.000001"))
                event = await emit_usage(
                    db,
                    tenant_id=tenant_id,
                    org_id=org_id,
                    usage_type="storage_gb_day",
                    quantity=gb,
                    occurred_at=datetime.now(UTC),
                    source="storage_sweep",
                    idempotency_key=f"storage:{org_id}:{day}",
                )
            if event is not None:
                emitted += 1
        except Exception:  # noqa: BLE001 — one bad org must not wedge the cron
            log.warning("cp_storage_sweep_org_failed", org_id=org_id, exc_info=True)
            continue
    return emitted


async def sweep_seats(
    db: AsyncSession,
    for_month: str | None = None,
    org_ids: list[str] | None = None,
) -> int:
    """Monthly active_learner_seat events per org. Key: seats:{org}:{YYYY-MM}.
    'Active' = org_members.status=active AND role=student (ADR: login activity
    not considered in v1). R258: `org_ids` narrows a targeted ops re-run and
    makes tests hermetic (mirrors sweep_storage)."""
    from app.models.organization import (
        MemberStatus,
        Organization,
        OrgMember,
        OrgRole,
        OrgStatus,
    )

    month = for_month or datetime.now(UTC).strftime("%Y-%m")
    rows = (
        await db.execute(
            select(
                Organization.id,
                Organization.tenant_id,
                func.count(func.distinct(OrgMember.user_id)),
            )
            .join(OrgMember, OrgMember.org_id == Organization.id)
            .where(
                Organization.status != OrgStatus.ARCHIVED,
                OrgMember.status == MemberStatus.ACTIVE,
                OrgMember.role == OrgRole.STUDENT,
                *([Organization.id.in_(org_ids)] if org_ids is not None else []),
            )
            .group_by(Organization.id, Organization.tenant_id)
        )
    ).all()
    emitted = 0
    for org_id, tenant_id, seats in rows:
        if seats == 0:
            continue
        # R169: isolate each org — one org's emit failure must not abort the
        # MONTHLY seat sweep (it fires only on the 1st, so an unguarded abort
        # loses a WHOLE month of seat billing platform-wide). Mirrors the
        # storage sweep above and expire_promotional/R168.
        try:
            async with db.begin_nested():
                event = await emit_usage(
                    db,
                    tenant_id=tenant_id,
                    org_id=org_id,
                    usage_type="active_learner_seat",
                    quantity=seats,
                    occurred_at=datetime.now(UTC),
                    source="seat_sweep",
                    idempotency_key=f"seats:{org_id}:{month}",
                )
            if event is not None:
                emitted += 1
        except Exception:  # noqa: BLE001 — one bad org must not wedge the cron
            log.warning("cp_seat_sweep_org_failed", org_id=org_id, exc_info=True)
            continue
    return emitted


async def flush_api_request_counters(db: AsyncSession) -> int:
    """Hourly: land the previous hour's Redis counters as api_request events.
    Key: apireq:{tenant}:{YYYYMMDDHH}; DEL on success (idempotency key guards
    the crash-between window)."""
    from app.core.redis import redis_pool

    try:
        r = redis_pool()
        now = datetime.now(UTC)
        now_bucket = now.strftime("%Y%m%d%H")
        # R53[1]: deleting a flushed bucket destroyed the live day window the
        # quota middleware MGETs — by late day most buckets were gone and
        # tenants sailed past max_api_requests_day. Keep buckets until they
        # can no longer be part of ANY tenant's current local day (a local
        # day never reaches back more than 24h; 25h matches the key TTL).
        # Re-scanning kept buckets is harmless: the emit idempotency key
        # (apireq:{tenant}:{bucket}) makes re-emission a no-op.
        delete_cutoff = (now - timedelta(hours=25)).strftime("%Y%m%d%H")
        emitted = 0
        async for key in r.scan_iter(match="cp:apireq:*", count=500):
            key_s = key.decode() if isinstance(key, bytes) else key
            _, _, tenant_id, bucket = key_s.split(":")
            if bucket >= now_bucket:
                continue  # current hour still accumulating
            count = int(await r.get(key_s) or 0)
            landed = count <= 0  # empty bucket = nothing to land
            if count > 0:
                # Attribution org: not tracked per-bucket — use the tenant's
                # first org for the org_id column (aggregate-level metric).
                from app.models.organization import Organization

                org_id = (
                    await db.execute(
                        select(Organization.id).where(Organization.tenant_id == tenant_id).limit(1)
                    )
                ).scalar_one_or_none()
                if org_id is not None:
                    occurred = datetime.strptime(bucket, "%Y%m%d%H").replace(tzinfo=UTC)
                    event = await emit_usage(
                        db,
                        tenant_id=tenant_id,
                        org_id=org_id,
                        usage_type="api_request",
                        quantity=count,
                        occurred_at=occurred,
                        source="api_metering",
                        idempotency_key=f"apireq:{tenant_id}:{bucket}",
                    )
                    landed = True
                    if event is not None:
                        emitted += 1
                else:
                    # R57[3]: an org-less tenant (freshly provisioned, counted
                    # via /tenants/{id}/... paths) has metered usage but no
                    # attribution org YET. Deleting the bucket would silently
                    # lose billable usage — keep it; a later run lands it once
                    # the org exists (TTL bounds the wait at 25h, an accepted
                    # loss only if the tenant never gains an org).
                    log.warning(
                        "cp_api_flush_no_org", tenant_id=tenant_id, bucket=bucket, count=count
                    )
            await db.commit()
            if landed and bucket < delete_cutoff:
                await r.delete(key_s)
        return emitted
    except Exception:  # noqa: BLE001 — Redis outage: flush retries next hour
        log.warning("cp_api_flush_skipped", exc_info=True)
        return 0
