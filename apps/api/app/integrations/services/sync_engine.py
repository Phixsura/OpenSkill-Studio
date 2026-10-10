"""Sync engine (ADR-018 §11): profiles, runs, cursor-checkpointed batches.

Correctness core (§11.3): each batch's staged writes AND the advanced
cursor_out commit in ONE transaction — destination-confirmed state by
construction. A crash re-runs from the last committed cursor; staged writes
are idempotent upserts on (connection_id, model, external_id) keyed by
raw_hash, so at-least-once + dedup. Tombstones only on full snapshots
(trigger='backfill'): an absent record in a delta is not a delete.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models import (
    BATCH_SIZE,
    CANONICAL_MODELS,
    FIELD_POLICIES,
    STALE_RUN_REAP_MINUTES,
    SYNC_DIRECTIONS,
    SYNC_SCHEDULES,
    IntegrationConnection,
    IntegrationProvider,
    MappingProfile,
    StagedRecord,
    SyncProfile,
    SyncRecordResult,
    SyncRun,
)
from app.integrations.registry import CONNECTORS
from app.integrations.services.mapping import apply_mapping

log = structlog.get_logger()

TOPIC_SYNC_RUN = "intg.sync.run"


def _payload_hash(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


# ── profile CRUD ──


class SyncProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        org_id: str,
        *,
        connection_id: str,
        name: str,
        model: str,
        direction: str,
        mapping_profile_id: str | None,
        schedule: str = "manual",
        field_policy: dict | None = None,
        options: dict | None = None,
    ) -> SyncProfile:
        if model not in CANONICAL_MODELS:
            raise AppError("SYNC_PROFILE_INVALID", f"unknown model: {model}", 422)
        if direction not in SYNC_DIRECTIONS:
            raise AppError("SYNC_PROFILE_INVALID", "bad direction", 422)
        if schedule not in SYNC_SCHEDULES:
            raise AppError("SYNC_PROFILE_INVALID", "bad schedule", 422)
        self._validate_field_policy(field_policy or {})
        conn = await self.db.get(IntegrationConnection, connection_id)
        if conn is None or conn.org_id != org_id:
            raise AppError("CONNECTION_NOT_FOUND", "Connection not found", 404)
        await self._check_capability(conn, model, direction)
        mapping_version = None
        if mapping_profile_id is not None:
            mp = await self.db.get(MappingProfile, mapping_profile_id)
            if mp is None or mp.org_id != org_id:
                raise AppError("MAPPING_NOT_FOUND", "Mapping profile not found", 404)
            if mp.model != model:
                raise AppError("SYNC_PROFILE_INVALID", "mapping model mismatch", 422)
            mapping_version = mp.version  # pin (§10.1)
        profile = SyncProfile(
            org_id=org_id,
            connection_id=connection_id,
            name=name,
            model=model,
            direction=direction,
            mapping_profile_id=mapping_profile_id,
            mapping_version=mapping_version,
            schedule=schedule,
            field_policy=field_policy or {},
            options=options or {},
        )
        try:
            # SAVEPOINT: a unique-index loser must not poison the session (R422).
            async with self.db.begin_nested():
                self.db.add(profile)
                await self.db.flush()
        except Exception as exc:
            raise AppError(
                "SYNC_PROFILE_EXISTS", "A profile for this connection/model/direction exists", 409
            ) from exc
        await self.db.refresh(profile)
        return profile

    @staticmethod
    def _validate_field_policy(policy: dict) -> None:
        for field, rule in policy.items():
            if not isinstance(field, str) or rule not in FIELD_POLICIES:
                raise AppError(
                    "SYNC_PROFILE_INVALID", f"bad field policy for {field!r}", 422
                )

    async def _check_capability(
        self, conn: IntegrationConnection, model: str, direction: str
    ) -> None:
        """Binding-time AND run-time capability gate (R82 re-check rule)."""
        provider = await self.db.get(IntegrationProvider, conn.provider_id)
        connector = CONNECTORS.get(provider.key) if provider else None
        if provider is None or connector is None:
            raise AppError("CAPABILITY_MISSING", "No connector for provider", 409)
        if not provider.enabled:
            # Review defect #4: a kill-switched provider must refuse new runs,
            # not just hide from the catalog listing.
            raise AppError("PROVIDER_DISABLED", f"Provider disabled: {provider.key}", 409)
        family = model.split(".", 1)[0]
        needed = set()
        if direction in ("pull", "bidirectional"):
            needed.add(f"{family}.read")
        if direction in ("push", "bidirectional"):
            needed.add(f"{family}.write")
        declared = set(provider.capabilities or [])
        if not needed <= declared or not needed <= set(connector.capabilities):
            raise AppError(
                "CAPABILITY_MISSING",
                f"connector lacks {sorted(needed - (declared & set(connector.capabilities)))}",
                409,
            )

    async def get(self, org_id: str, profile_id: str) -> SyncProfile:
        p = await self.db.get(SyncProfile, profile_id)
        if p is None or p.org_id != org_id:
            raise AppError("SYNC_PROFILE_NOT_FOUND", "Sync profile not found", 404)
        return p

    async def list(self, org_id: str) -> list[SyncProfile]:
        return list(
            (
                await self.db.execute(
                    select(SyncProfile)
                    .where(SyncProfile.org_id == org_id)
                    .order_by(SyncProfile.created_at)
                )
            ).scalars()
        )

    async def trigger(self, org_id: str, profile_id: str, *, trigger: str = "manual") -> SyncRun:
        """Idempotent: a live run is returned instead of a second one."""
        profile = await self.get(org_id, profile_id)
        if not profile.enabled:
            raise AppError("SYNC_PROFILE_DISABLED", "Profile is disabled", 409)
        conn = await self.db.get(IntegrationConnection, profile.connection_id)
        if conn is None or conn.status not in ("active", "degraded", "pending"):
            raise AppError("SYNC_CONNECTION_UNAVAILABLE", "Connection not schedulable", 409)
        await self._check_capability(conn, profile.model, profile.direction)  # run-time re-check
        # Opportunistic reap (review defect #6): a crashed worker's stale
        # 'running' row would otherwise block this profile forever — no cron
        # needed, the next trigger clears it.
        await reap_stale_runs(self.db)
        live = (
            await self.db.execute(
                select(SyncRun).where(
                    SyncRun.profile_id == profile.id,
                    SyncRun.status.in_(("queued", "running")),
                )
            )
        ).scalar_one_or_none()
        if live is not None:
            return live
        cursor_in = {} if trigger == "backfill" else await self._last_cursor(profile.id)
        run = SyncRun(
            profile_id=profile.id, status="queued", trigger=trigger, cursor_in=cursor_in
        )
        try:
            async with self.db.begin_nested():
                self.db.add(run)
                await self.db.flush()
        except Exception:
            # Unique live-run index arbitrated a race — return the winner.
            live = (
                await self.db.execute(
                    select(SyncRun).where(
                        SyncRun.profile_id == profile.id,
                        SyncRun.status.in_(("queued", "running")),
                    )
                )
            ).scalar_one_or_none()
            if live is not None:
                return live
            raise
        from app.controlplane.models.outbox import enqueue

        enqueue(self.db, TOPIC_SYNC_RUN, {"run_id": run.id})
        await self.db.refresh(run)
        return run

    async def _last_cursor(self, profile_id: str) -> dict:
        last = (
            await self.db.execute(
                select(SyncRun.cursor_out)
                .where(SyncRun.profile_id == profile_id, SyncRun.status == "succeeded")
                .order_by(SyncRun.finished_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        return last or {}

    async def cancel(self, org_id: str, run_id: str) -> SyncRun:
        run, profile = await self._run_scoped(org_id, run_id)
        if run.status not in ("queued", "running"):
            raise AppError("SYNC_RUN_NOT_CANCELLABLE", "Run already finished", 409)
        run.status = "cancelled"
        run.finished_at = datetime.now(UTC)
        await self.db.flush()
        return run

    async def _run_scoped(self, org_id: str, run_id: str) -> tuple[SyncRun, SyncProfile]:
        run = await self.db.get(SyncRun, run_id)
        profile = await self.db.get(SyncProfile, run.profile_id) if run else None
        if run is None or profile is None or profile.org_id != org_id:
            raise AppError("SYNC_RUN_NOT_FOUND", "Run not found", 404)
        return run, profile

    async def list_runs(self, org_id: str, profile_id: str | None = None) -> list[SyncRun]:
        q = (
            select(SyncRun)
            .join(SyncProfile, SyncProfile.id == SyncRun.profile_id)
            .where(SyncProfile.org_id == org_id)
            .order_by(SyncRun.created_at.desc())
            .limit(100)
        )
        if profile_id:
            q = q.where(SyncRun.profile_id == profile_id)
        return list((await self.db.execute(q)).scalars())

    async def run_records(
        self, org_id: str, run_id: str, outcome: str | None = None
    ) -> list[SyncRecordResult]:
        run, _ = await self._run_scoped(org_id, run_id)
        q = (
            select(SyncRecordResult)
            .where(SyncRecordResult.run_id == run.id)
            .order_by(SyncRecordResult.created_at)
            .limit(1000)
        )
        if outcome:
            q = q.where(SyncRecordResult.outcome == outcome)
        return list((await self.db.execute(q)).scalars())


# ── engine execution (outbox handler + inline test driver) ──


async def execute_run(db: AsyncSession, run_id: str) -> None:
    """Pull-direction v1 engine. Idempotent: a finished/cancelled run no-ops;
    a queued run (re)starts from run.cursor_out or cursor_in."""
    # Atomic claim: only a QUEUED run (or a RUNNING one whose heartbeat went
    # stale — crashed worker) may be picked up; a redelivered outbox message
    # for a live run is a no-op instead of a double-execution.
    stale_cutoff = datetime.now(UTC) - timedelta(minutes=STALE_RUN_REAP_MINUTES)
    claimed = (
        await db.execute(
            update(SyncRun)
            .where(
                SyncRun.id == run_id,
                (SyncRun.status == "queued")
                | ((SyncRun.status == "running") & (SyncRun.heartbeat_at < stale_cutoff)),
            )
            .values(status="running", heartbeat_at=datetime.now(UTC))
            .returning(SyncRun.id)
        )
    ).scalar_one_or_none()
    await db.commit()
    if claimed is None:
        return
    run = await db.get(SyncRun, run_id)
    profile = await db.get(SyncProfile, run.profile_id)
    conn = await db.get(IntegrationConnection, profile.connection_id)
    provider = await db.get(IntegrationProvider, conn.provider_id)
    connector = CONNECTORS.get(provider.key) if provider else None
    if connector is None or not hasattr(connector, "read"):
        await _finish(db, run, "failed", error={"class": "connector_missing"})
        return
    mapping_doc = None
    if profile.mapping_profile_id:
        mp = await db.get(MappingProfile, profile.mapping_profile_id)
        if mp is None or (
            profile.mapping_version is not None and mp.version != profile.mapping_version
        ):
            await _finish(db, run, "failed", error={"class": "mapping_version_drift"})
            return
        mapping_doc = mp.document

    run.started_at = run.started_at or datetime.now(UTC)
    stats = dict(run.stats or {})
    for key in ("read", "created", "updated", "unchanged", "tombstoned", "conflicts", "errors"):
        stats.setdefault(key, 0)
    state = dict(run.cursor_out or {}) or dict(run.cursor_in or {})
    seen_external_ids: set[str] = set()
    await db.commit()  # publish 'running' + heartbeat before the long read

    from app.integrations.registry import ConnCtx

    ctx = ConnCtx(connection_id=conn.id, config=conn.config or {}, base_url=conn.base_url)
    try:
        async for batch in connector.read(ctx, profile.model, state):
            records = batch.get("records", [])
            next_state = batch.get("state", state)
            stats["read"] += len(records)
            for raw in records[: BATCH_SIZE * 2]:
                outcome, detail = await _apply_record(
                    db, run, profile, conn, mapping_doc, raw, seen_external_ids
                )
                stats[outcome] = stats.get(outcome, 0) + 1
            # ONE txn: staged writes + advanced cursor + stats (§11.3).
            # Fresh dict copies every time: SQLAlchemy detects JSONB changes
            # by object identity, so re-assigning the same mutated dict is
            # silently a no-op UPDATE (the final batch's stats vanish).
            state = next_state
            run.cursor_out = dict(state)
            run.stats = dict(stats)
            run.heartbeat_at = datetime.now(UTC)
            await db.commit()
    except AppError as exc:
        await _finish(db, run, "failed", error={"class": exc.code})
        return
    except Exception as exc:  # connector bug / network — retryable by re-trigger
        log.warning("sync_run_crashed", run_id=run.id, error=type(exc).__name__)
        await _finish(db, run, "failed", error={"class": type(exc).__name__[:60]})
        return

    # Tombstone pass — FULL SNAPSHOTS ONLY (§11.3).
    if run.trigger == "backfill" and seen_external_ids is not None:
        rows = (
            await db.execute(
                select(StagedRecord).where(
                    StagedRecord.connection_id == conn.id,
                    StagedRecord.model == profile.model,
                    StagedRecord.status == "active",
                )
            )
        ).scalars()
        for staged in rows:
            if staged.external_id not in seen_external_ids:
                staged.status = "tombstoned"
                staged.last_seen_run_id = run.id
                stats["tombstoned"] += 1
                db.add(
                    SyncRecordResult(
                        run_id=run.id,
                        external_id=staged.external_id,
                        model=profile.model,
                        outcome="tombstoned",
                    )
                )
    status = "partial" if stats.get("conflicts") or stats.get("errors") else "succeeded"
    run.stats = dict(stats)
    await _finish(db, run, status)


async def _apply_record(
    db: AsyncSession,
    run: SyncRun,
    profile: SyncProfile,
    conn: IntegrationConnection,
    mapping_doc: dict | None,
    raw: dict,
    seen: set[str],
) -> tuple[str, dict]:
    external_id = str(raw.get("external_id") or raw.get("sourcedId") or raw.get("id") or "")
    if not external_id or len(external_id) > 255:
        db.add(
            SyncRecordResult(
                run_id=run.id,
                external_id=external_id[:255] or "?",
                model=profile.model,
                outcome="error",
                detail={"code": "missing_external_id"},
            )
        )
        return "errors", {}
    if external_id in seen:
        db.add(
            SyncRecordResult(
                run_id=run.id,
                external_id=external_id,
                model=profile.model,
                outcome="conflict",
                conflict_class="duplicate_external_id",
            )
        )
        return "conflicts", {}
    seen.add(external_id)

    if mapping_doc is not None:
        mapped, errors = apply_mapping(mapping_doc, raw)
        if errors:
            db.add(
                SyncRecordResult(
                    run_id=run.id,
                    external_id=external_id,
                    model=profile.model,
                    outcome="conflict",
                    conflict_class=(
                        "enum_unmapped"
                        if any(e["code"] == "enum_unmapped" for e in errors)
                        else "schema_invalid"
                    ),
                    detail={"errors": errors[:10]},
                )
            )
            return "conflicts", {}
    else:
        mapped = raw

    new_hash = _payload_hash(mapped)
    staged = (
        await db.execute(
            select(StagedRecord).where(
                StagedRecord.connection_id == conn.id,
                StagedRecord.model == profile.model,
                StagedRecord.external_id == external_id,
            )
        )
    ).scalar_one_or_none()
    if staged is None:
        db.add(
            StagedRecord(
                connection_id=conn.id,
                model=profile.model,
                external_id=external_id,
                payload=mapped,
                raw_hash=new_hash,
                status="active",
                first_seen_run_id=run.id,
                last_seen_run_id=run.id,
            )
        )
        db.add(
            SyncRecordResult(
                run_id=run.id, external_id=external_id, model=profile.model, outcome="created"
            )
        )
        return "created", {}
    staged.last_seen_run_id = run.id
    if staged.raw_hash == new_hash and staged.status == "active":
        return "unchanged", {}  # counter only — no result row (§11.4)

    # Echo suppression (§11.5): inbound change equal to our last outbound
    # write within 24h is a reflection, not a change.
    lo = staged.last_outbound or {}
    if lo.get("fields_hash") == new_hash:
        written_at = lo.get("written_at")
        try:
            dt = datetime.fromisoformat(written_at) if written_at else None
        except ValueError:
            dt = None
        if dt is not None and datetime.now(UTC) - dt <= timedelta(hours=24):
            staged.payload = mapped
            staged.raw_hash = new_hash
            return "unchanged", {}

    # Field-level source-of-truth (§11.5) for updates.
    policy = profile.field_policy or {}
    default_rule = policy.get("_default", "theirs")
    merged = dict(staged.payload or {})
    conflicted = False
    for key, incoming in mapped.items():
        rule = policy.get(key, default_rule)
        current = merged.get(key)
        if rule == "ours":
            continue  # we own it; inbound never overwrites
        if rule == "theirs":
            merged[key] = incoming
        elif rule == "prefer_ours_unless_blank":
            if current in (None, "", []):
                merged[key] = incoming
        elif rule == "most_recent":
            ours_ts = _ts(merged.get("_updated_at"))
            theirs_ts = _ts(raw.get("updated_at") or raw.get("dateLastModified"))
            if ours_ts is None or theirs_ts is None or ours_ts == theirs_ts:
                conflicted = True
                db.add(
                    SyncRecordResult(
                        run_id=run.id,
                        external_id=external_id,
                        model=profile.model,
                        outcome="conflict",
                        conflict_class="clock_unresolvable",
                        detail={"field": key},
                    )
                )
                continue
            if theirs_ts > ours_ts:
                merged[key] = incoming
    # Drop keys the source no longer sends only under pure-theirs policy.
    if default_rule == "theirs" and not policy:
        merged = mapped
    if conflicted:
        return "conflicts", {}
    staged.payload = merged
    staged.raw_hash = _payload_hash(merged)
    staged.status = "active"
    db.add(
        SyncRecordResult(
            run_id=run.id, external_id=external_id, model=profile.model, outcome="updated"
        )
    )
    return "updated", {}


def _ts(value) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


async def _finish(db: AsyncSession, run: SyncRun, status: str, *, error: dict | None = None) -> None:
    run.status = status
    run.error = error
    run.finished_at = datetime.now(UTC)
    await db.commit()
    profile = await db.get(SyncProfile, run.profile_id)
    if profile is not None:
        try:
            from app.integrations.facade import emit_event

            await emit_event(
                db,
                profile.org_id,
                "integration.sync.completed",
                subject=run.id,
                data={"profile_id": profile.id, "status": status, "stats": run.stats or {}},
            )
            await db.commit()
        except Exception:
            log.warning("mesh_emit_failed", event="integration.sync.completed", run_id=run.id)


async def reap_stale_runs(db: AsyncSession) -> int:
    """Crash-retry pin (R85): a running run with a stale heartbeat is failed
    so the next trigger can start cleanly from the committed cursor."""
    cutoff = datetime.now(UTC) - timedelta(minutes=STALE_RUN_REAP_MINUTES)
    res = await db.execute(
        update(SyncRun)
        .where(SyncRun.status == "running", SyncRun.heartbeat_at < cutoff)
        .values(status="failed", error={"class": "stale_heartbeat"}, finished_at=datetime.now(UTC))
        .returning(SyncRun.id)
    )
    return len(res.all())
