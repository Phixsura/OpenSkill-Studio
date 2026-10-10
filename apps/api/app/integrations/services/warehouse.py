"""Governed warehouse export (ADR-018 §16.2, research S8.4).

Governance invariants:
- Tenant boundary lives in the EXTRACTION QUERY (org_id predicate injected
  here), never delegated to the destination.
- The allowlist is enforced at serialization: a row dict is BUILT from the
  allowlist, so an un-listed field is structurally absent (R82 pattern —
  the test generates the field universe and asserts coverage).
- Anonymization (hash with a per-org salt / drop) runs before bytes leave.
- Exports are incremental: the cursor advances only after a successful run;
  freshness (cursor_to, generated_at) is first-class in the manifest.

The byte sink is injectable (`writer`): the API/worker use S3; tests use an
in-memory writer. Parts are NDJSON.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Protocol

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.exceptions import AppError
from app.integrations.models import IntegrationEvent
from app.integrations.models.export import (
    ANONYMIZE_MODES,
    EXPORT_PAGE_ROWS,
    EXPORT_SCHEDULES,
    ExportRun,
    ExportStream,
)

log = structlog.get_logger()

SCHEMA_VERSION = 1


class PartWriter(Protocol):
    async def write(self, key: str, content: bytes) -> None: ...


# ── dataset definitions: (field universe, cursor field, extractor) ──


async def _extract_events(
    db: AsyncSession, org_id: str, since: str | None, limit: int
) -> list[dict[str, Any]]:
    q = (
        select(IntegrationEvent)
        .where(IntegrationEvent.org_id == org_id)
        .order_by(IntegrationEvent.time.asc(), IntegrationEvent.id.asc())
        .limit(limit)
    )
    if since:
        q = q.where(IntegrationEvent.id > since)  # ULID ids are time-ordered
    rows = (await db.execute(q)).scalars().all()
    return [
        {
            "id": e.id,
            "type": e.type,
            "subject": e.subject,
            "time": e.time.isoformat() if e.time else None,
            "_cursor": e.id,
        }
        for e in rows
    ]


async def _extract_enrollments(
    db: AsyncSession, org_id: str, since: str | None, limit: int
) -> list[dict[str, Any]]:
    from app.models.cohort import Cohort, CohortMember

    q = (
        select(CohortMember, Cohort.name)
        .join(Cohort, Cohort.id == CohortMember.cohort_id)
        .where(Cohort.org_id == org_id)
        .order_by(CohortMember.id.asc())
        .limit(limit)
    )
    if since:
        q = q.where(CohortMember.id > since)
    rows = (await db.execute(q)).all()
    return [
        {
            "id": m.id,
            "cohort_id": m.cohort_id,
            "cohort_name": name,
            "user_id": m.user_id,
            "role": m.role.value if hasattr(m.role, "value") else str(m.role),
            "joined_at": m.joined_at.isoformat() if m.joined_at else None,
            "_cursor": m.id,
        }
        for m, name in rows
    ]


# dataset -> (field universe, extractor, default allowlist)
DATASETS: dict[str, dict] = {
    "events": {
        "fields": frozenset({"id", "type", "subject", "time"}),
        "extract": _extract_events,
        "default_allowlist": ["id", "type", "subject", "time"],
        # The CloudEvents `data` payload is deliberately NOT exportable in
        # v1: every key inside would need its own allowlist entry (the R82
        # trap at warehouse scale) — a later phase adds per-key selection.
    },
    "enrollments": {
        "fields": frozenset({"id", "cohort_id", "cohort_name", "user_id", "role", "joined_at"}),
        "extract": _extract_enrollments,
        "default_allowlist": ["id", "cohort_id", "cohort_name", "user_id", "role", "joined_at"],
        "default_anonymize": {"user_id": "hash"},
    },
}


def _org_salt(org_id: str) -> str:
    from app.config import settings

    return hashlib.sha256(f"{settings.jwt_secret}:{org_id}:export".encode()).hexdigest()[:16]


class WarehouseExportService:
    def __init__(self, db: AsyncSession, writer: PartWriter | None = None):
        self.db = db
        self.writer = writer

    # ── stream CRUD ──

    async def create_stream(
        self,
        org_id: str,
        *,
        name: str,
        dataset: str,
        field_allowlist: list[str] | None = None,
        anonymize: dict | None = None,
        schedule: str = "manual",
    ) -> ExportStream:
        spec = DATASETS.get(dataset)
        if spec is None:
            raise AppError("EXPORT_DATASET_UNKNOWN", f"unknown dataset: {dataset}", 422)
        if schedule not in EXPORT_SCHEDULES:
            raise AppError("EXPORT_CONFIG_INVALID", "bad schedule", 422)
        allowlist = field_allowlist or list(spec["default_allowlist"])
        bad = [f for f in allowlist if f not in spec["fields"]]
        if bad:
            raise AppError(
                "EXPORT_FIELD_NOT_ALLOWED",
                f"fields not in dataset universe: {bad}",
                422,
            )
        anon = anonymize if anonymize is not None else dict(spec.get("default_anonymize", {}))
        for field, mode in anon.items():
            if field not in spec["fields"] or mode not in ANONYMIZE_MODES:
                raise AppError("EXPORT_CONFIG_INVALID", f"bad anonymize entry {field!r}", 422)
        stream = ExportStream(
            org_id=org_id,
            name=name,
            dataset=dataset,
            field_allowlist=allowlist,
            anonymize=anon,
            schedule=schedule,
        )
        try:
            async with self.db.begin_nested():
                self.db.add(stream)
                await self.db.flush()
        except Exception as exc:
            raise AppError("EXPORT_NAME_TAKEN", "A stream with this name exists", 409) from exc
        await self.db.refresh(stream)
        return stream

    async def get_stream(self, org_id: str, stream_id: str) -> ExportStream:
        s = await self.db.get(ExportStream, stream_id)
        if s is None or s.org_id != org_id:
            raise AppError("EXPORT_STREAM_NOT_FOUND", "Stream not found", 404)
        return s

    async def list_streams(self, org_id: str) -> list[ExportStream]:
        return list(
            (
                await self.db.execute(
                    select(ExportStream)
                    .where(ExportStream.org_id == org_id)
                    .order_by(ExportStream.created_at)
                )
            ).scalars()
        )

    async def list_runs(self, org_id: str, stream_id: str) -> list[ExportRun]:
        stream = await self.get_stream(org_id, stream_id)
        return list(
            (
                await self.db.execute(
                    select(ExportRun)
                    .where(ExportRun.stream_id == stream.id)
                    .order_by(ExportRun.created_at.desc())
                    .limit(50)
                )
            ).scalars()
        )

    # ── run ──

    def _project_row(self, stream: ExportStream, row: dict, salt: str) -> dict:
        """Allowlist-BUILT projection + anonymization. The output dict is
        constructed FROM the allowlist — unlisted fields cannot leak."""
        out: dict[str, Any] = {}
        anon = stream.anonymize or {}
        for field in stream.field_allowlist:
            if anon.get(field) == "drop":
                continue
            value = row.get(field)
            if anon.get(field) == "hash" and value is not None:
                value = hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:32]
            out[field] = value
        return out

    async def run_export(self, org_id: str, stream_id: str) -> ExportRun:
        stream = await self.get_stream(org_id, stream_id)
        if not stream.enabled:
            raise AppError("EXPORT_STREAM_DISABLED", "Stream is disabled", 409)
        if self.writer is None:
            raise AppError("EXPORT_WRITER_MISSING", "No destination writer configured", 500)
        spec = DATASETS[stream.dataset]
        run = ExportRun(
            stream_id=stream.id,
            cursor_from=dict(stream.cursor or {}),
        )
        self.db.add(run)
        await self.db.flush()

        salt = _org_salt(org_id)
        since = (stream.cursor or {}).get("last_id")
        total = 0
        parts: list[str] = []
        part_no = 0
        last_cursor = since
        base = f"exports/{org_id}/{stream.dataset}/{run.id}"
        try:
            while True:
                rows = await spec["extract"](self.db, org_id, last_cursor, EXPORT_PAGE_ROWS)
                if not rows:
                    break
                lines = []
                for row in rows:
                    last_cursor = row.pop("_cursor", last_cursor)
                    lines.append(
                        json.dumps(
                            self._project_row(stream, row, salt), separators=(",", ":")
                        )
                    )
                part_key = f"{base}/part-{part_no:05d}.ndjson"
                await self.writer.write(part_key, ("\n".join(lines) + "\n").encode())
                parts.append(part_key)
                total += len(rows)
                part_no += 1
                if len(rows) < EXPORT_PAGE_ROWS:
                    break
            manifest_key = f"{base}/manifest.json"
            manifest = {
                "stream_id": stream.id,
                "dataset": stream.dataset,
                "schema_version": SCHEMA_VERSION,
                "fields": [
                    f
                    for f in stream.field_allowlist
                    if (stream.anonymize or {}).get(f) != "drop"
                ],
                "cursor_from": run.cursor_from,
                "cursor_to": {"last_id": last_cursor},
                "row_count": total,
                "parts": parts,
                "generated_at": datetime.now(UTC).isoformat(),
            }
            await self.writer.write(manifest_key, json.dumps(manifest, indent=2).encode())
        except AppError:
            raise
        except Exception as exc:
            run.status = "failed"
            run.error = type(exc).__name__[:200]
            run.finished_at = datetime.now(UTC)
            await self.db.flush()
            return run
        run.status = "succeeded"
        run.row_count = total
        run.parts = parts
        run.manifest_key = manifest_key
        run.cursor_to = {"last_id": last_cursor}
        run.finished_at = datetime.now(UTC)
        # Cursor advances ONLY on success — a failed run re-exports the span.
        stream.cursor = {"last_id": last_cursor}
        await self.db.flush()
        return run


async def sweep_scheduled_exports(db: AsyncSession, writer: PartWriter) -> int:
    """Worker cron (R16 — same gap class as scheduled syncs): daily export
    streams run when their last run is older than a day."""
    from datetime import timedelta

    from app.integrations.models.export import ExportRun

    streams = (
        await db.execute(
            select(ExportStream).where(
                ExportStream.enabled.is_(True), ExportStream.schedule == "daily"
            )
        )
    ).scalars().all()
    ran = 0
    now = datetime.now(UTC)
    for stream in streams:
        last = (
            await db.execute(
                select(ExportRun.created_at)
                .where(ExportRun.stream_id == stream.id)
                .order_by(ExportRun.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if last is not None:
            if last.tzinfo is None:
                last = last.replace(tzinfo=UTC)
            if now - last < timedelta(days=1):
                continue
        try:
            await WarehouseExportService(db, writer=writer).run_export(
                stream.org_id, stream.id
            )
            ran += 1
        except AppError as exc:
            log.warning("scheduled_export_skipped", stream_id=stream.id, code=exc.code)
    return ran


class S3PartWriter:
    """Production writer (API/worker)."""

    async def write(self, key: str, content: bytes) -> None:
        from app.config import settings
        from app.core.storage import get_s3_client

        async for client in get_s3_client():
            await client.put_object(
                Bucket=settings.s3_bucket,
                Key=key,
                Body=content,
                ContentType=(
                    "application/json" if key.endswith(".json") else "application/x-ndjson"
                ),
            )


def _ulid() -> str:  # kept for import stability in future phases
    return str(ULID())
