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
import re
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.exceptions import AppError
from app.integrations.models import IntegrationEvent
from app.integrations.models.export import (
    ANONYMIZE_MODES,
    EXPORT_FORMATS,
    EXPORT_PAGE_ROWS,
    EXPORT_SCHEDULES,
    ExportRun,
    ExportStream,
)

log = structlog.get_logger()

SCHEMA_VERSION = 1


def _parquet_available() -> bool:
    """R486: pyarrow is an optional extra — parquet streams are refused at
    CONFIG time when it is missing, never discovered mid-run."""
    try:
        import pyarrow  # noqa: F401
        import pyarrow.parquet  # noqa: F401
    except ImportError:
        return False
    return True


class ParquetSchemaDriftError(Exception):
    """R508: a later page's values cannot conform to the run's pinned
    column types — fail the RUN terminally rather than emit parts a
    dataset reader cannot merge."""


def _parquet_bytes(
    rows: list[dict[str, Any]],
    columns: list[str],
    pinned: dict[str, Any] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    """Serialize projected rows to a parquet part.

    Column set comes from the ALLOWLIST (same universe as the NDJSON path —
    the R82 projection already dropped un-listed fields). Types are inferred
    by pyarrow; a column whose values mix incompatible types (possible for
    `data.<key>` payload selections) falls back to utf8 with JSON-encoded
    non-scalars rather than failing the run.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    def _norm(v: Any) -> Any:
        # Scalars keep their types; dict/list values are ALWAYS JSON-encoded
        # strings (R502, property-found: an empty dict infers as a childless
        # struct that parquet cannot WRITE, and heterogeneous structs would
        # give every part a different schema anyway).
        if v is None or isinstance(v, (bool, int, float, str)):
            return v
        return json.dumps(v, separators=(",", ":"), default=str)

    def _col(name: str) -> list[Any]:
        return [_norm(r.get(name)) for r in rows]

    arrays: dict[str, pa.Array] = {}
    out_types: dict[str, Any] = {}
    for name in columns:
        values = _col(name)
        want = (pinned or {}).get(name)
        try:
            arr = pa.array(values, type=want)
        except (pa.ArrowInvalid, pa.ArrowTypeError, pa.ArrowNotImplementedError) as exc:
            if want is not None and not pa.types.is_string(want):
                # R508 (review finding #3): the run's schema is PINNED by its
                # first part — a later page that cannot conform must fail the
                # run, not silently emit a differently-typed part the dataset
                # reader cannot merge with the ones already written.
                raise ParquetSchemaDriftError(f"column {name!r} drifted from {want}") from exc
            # first part (or pinned utf8): mixed scalars fall back to utf8
            arr = pa.array(
                [None if v is None else (v if isinstance(v, str) else str(v)) for v in values],
                type=pa.string(),
            )
        if pinned is None and pa.types.is_null(arr.type):
            # an all-None first page must not pin the unmergeable `null`
            # type — later pages with values would drift immediately
            arr = arr.cast(pa.string())
        arrays[name] = arr
        out_types[name] = arr.type
    table = pa.table(arrays)
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink, compression="snappy")
    return sink.getvalue().to_pybytes(), out_types


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
            # R130: carried for data.<key> projection only — the projection
            # is BUILT from the allowlist, so the raw payload cannot leak.
            "data": e.data or {},
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
        # The WHOLE CloudEvents `data` payload is deliberately not a field:
        # R130 adds per-key selection via explicit `data.<key>` allowlist
        # entries instead (the R82 trap at warehouse scale).
    },
    "enrollments": {
        "fields": frozenset({"id", "cohort_id", "cohort_name", "user_id", "role", "joined_at"}),
        "extract": _extract_enrollments,
        "default_allowlist": ["id", "cohort_id", "cohort_name", "user_id", "role", "joined_at"],
        "default_anonymize": {"user_id": "hash"},
    },
}


_DATA_KEY_RE = re.compile(r"^data\.[a-zA-Z0-9_-]{1,64}$")
MAX_DATA_KEYS = 20
MAX_STREAMS_PER_ORG = 20  # R262: bounds the shared hourly sweep's fan-out


def _check_fields(dataset: str, spec: dict, fields, *, what: str) -> None:
    """R130: per-key `data` selection. The whole CloudEvents payload is
    still NOT exportable — only explicit `data.<key>` entries (events
    dataset only, capped) join the plain field universe."""
    dotted = [f for f in fields if isinstance(f, str) and f.startswith("data.")]
    plain_bad = [
        f
        for f in fields
        if f not in spec["fields"] and not (dataset == "events" and _DATA_KEY_RE.fullmatch(str(f)))
    ]
    if plain_bad:
        raise AppError(
            "EXPORT_FIELD_NOT_ALLOWED",
            f"{what} not in dataset universe: {plain_bad}",
            422,
        )
    if len(dotted) > MAX_DATA_KEYS:
        raise AppError("EXPORT_CONFIG_INVALID", f"at most {MAX_DATA_KEYS} data.<key> entries", 422)


def _check_exported_columns(allowlist: list, anonymize: dict) -> None:
    """R502 (property-found): a config whose anonymize DROPS every allowed
    field exports empty objects — and the parquet writer cannot even carry
    the row count without columns. Refuse at config time for both formats."""
    if not [f for f in allowlist if (anonymize or {}).get(f) != "drop"]:
        raise AppError("EXPORT_CONFIG_INVALID", "every field is dropped — nothing to export", 422)


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
        part_format: str = "ndjson",
    ) -> ExportStream:
        spec = DATASETS.get(dataset)
        if spec is None:
            raise AppError("EXPORT_DATASET_UNKNOWN", f"unknown dataset: {dataset}", 422)
        if schedule not in EXPORT_SCHEDULES:
            raise AppError("EXPORT_CONFIG_INVALID", "bad schedule", 422)
        self._check_format(part_format)
        allowlist = field_allowlist or list(spec["default_allowlist"])
        _check_fields(dataset, spec, allowlist, what="fields")
        anon = anonymize if anonymize is not None else dict(spec.get("default_anonymize", {}))
        _check_fields(dataset, spec, anon.keys(), what="anonymize fields")
        for mode in anon.values():
            if mode not in ANONYMIZE_MODES:
                raise AppError("EXPORT_CONFIG_INVALID", "bad anonymize mode", 422)
        _check_exported_columns(allowlist, anon)
        # R262 (R260 class): the hourly sweep visits every enabled stream
        # across every org — bound per-org sprawl, race-proof under the lock.
        from app.models.organization import Organization as _Org

        await self.db.execute(select(_Org.id).where(_Org.id == org_id).with_for_update())
        count = len(
            (
                await self.db.execute(select(ExportStream.id).where(ExportStream.org_id == org_id))
            ).all()
        )
        if count >= MAX_STREAMS_PER_ORG:
            raise AppError("EXPORT_LIMIT_REACHED", "Too many export streams for this org", 422)
        stream = ExportStream(
            org_id=org_id,
            name=name,
            dataset=dataset,
            field_allowlist=allowlist,
            anonymize=anon,
            schedule=schedule,
            format=part_format,
        )
        try:
            async with self.db.begin_nested():
                self.db.add(stream)
                await self.db.flush()
        except Exception as exc:
            raise AppError("EXPORT_NAME_TAKEN", "A stream with this name exists", 409) from exc
        await self.db.refresh(stream)
        return stream

    async def update_stream(
        self,
        org_id: str,
        stream_id: str,
        *,
        field_allowlist: list[str] | None = None,
        anonymize: dict | None = None,
        schedule: str | None = None,
        enabled: bool | None = None,
        part_format: str | None = None,
    ) -> ExportStream:
        """R81: edit a stream in place — same universe/anonymize validation
        as create. The dataset is immutable (cursor semantics differ per
        dataset); narrowing the allowlist takes effect on the NEXT run."""
        stream = await self.get_stream(org_id, stream_id)
        spec = DATASETS[stream.dataset]
        if field_allowlist is not None:
            if not field_allowlist:
                raise AppError("EXPORT_FIELD_NOT_ALLOWED", "allowlist empty", 422)
            _check_fields(stream.dataset, spec, field_allowlist, what="fields")
            stream.field_allowlist = list(field_allowlist)
        if anonymize is not None:
            _check_fields(stream.dataset, spec, anonymize.keys(), what="anonymize fields")
            for mode in anonymize.values():
                if mode not in ANONYMIZE_MODES:
                    raise AppError("EXPORT_CONFIG_INVALID", "bad anonymize mode", 422)
            stream.anonymize = dict(anonymize)
        if schedule is not None:
            if schedule not in EXPORT_SCHEDULES:
                raise AppError("EXPORT_CONFIG_INVALID", "bad schedule", 422)
            stream.schedule = schedule
        if enabled is not None:
            stream.enabled = enabled
        # R508 (review finding #2): validate the drop-universe only when the
        # fields THEMSELVES change — an unconditional check bricked legacy
        # all-dropped streams out of the exact remediation PATCH
        # ({enabled:false} / a fixed allowlist) this rule exists to drive.
        if field_allowlist is not None or anonymize is not None:
            _check_exported_columns(stream.field_allowlist, stream.anonymize or {})
        if part_format is not None:
            self._check_format(part_format)
            stream.format = part_format
        await self.db.flush()
        return stream

    @staticmethod
    def _check_format(part_format: str) -> None:
        if part_format not in EXPORT_FORMATS:
            raise AppError("EXPORT_CONFIG_INVALID", "bad format", 422)
        if part_format == "parquet" and not _parquet_available():
            raise AppError(
                "EXPORT_FORMAT_UNAVAILABLE",
                "parquet support is not installed on this server",
                422,
            )

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
            if field.startswith("data."):  # R130 per-key payload selection
                value = (row.get("data") or {}).get(field[5:])
            else:
                value = row.get(field)
            if anon.get(field) == "hash" and value is not None:
                value = hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:32]
            out[field] = value
        return out

    async def run_export(self, org_id: str, stream_id: str) -> ExportRun:
        stream = await self.get_stream(org_id, stream_id)
        # R208: serialize runs per stream. A manual trigger racing the hourly
        # sweep (or a double-click) would otherwise read the SAME cursor —
        # both re-export the span, and whichever transaction commits LAST can
        # regress stream.cursor (its last_cursor may be older), making the
        # NEXT run re-export the whole span again. The row lock makes the
        # read-cursor → export → advance-cursor sequence atomic per stream.
        await self.db.execute(
            select(ExportStream.id).where(ExportStream.id == stream.id).with_for_update()
        )
        await self.db.refresh(stream)  # re-read cursor under the lock
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
        # R486: format=parquet refuses at config time when pyarrow is absent,
        # but guard the run too (the extra can be uninstalled under a stream).
        fmt = getattr(stream, "format", None) or "ndjson"
        if fmt == "parquet" and not _parquet_available():
            run.status = "failed"
            run.error = "EXPORT_FORMAT_UNAVAILABLE"
            run.finished_at = datetime.now(UTC)
            await self.db.flush()
            return run
        exported_columns = [
            f for f in stream.field_allowlist if (stream.anonymize or {}).get(f) != "drop"
        ]
        parquet_types: dict | None = None  # pinned by the run's FIRST part (R508)
        try:
            while True:
                rows = await spec["extract"](self.db, org_id, last_cursor, EXPORT_PAGE_ROWS)
                if not rows:
                    break
                projected = []
                for row in rows:
                    last_cursor = row.pop("_cursor", last_cursor)
                    projected.append(self._project_row(stream, row, salt))
                if fmt == "parquet":
                    part_key = f"{base}/part-{part_no:05d}.parquet"
                    content, parquet_types = _parquet_bytes(
                        projected, exported_columns, pinned=parquet_types
                    )
                else:
                    part_key = f"{base}/part-{part_no:05d}.ndjson"
                    lines = [json.dumps(p, separators=(",", ":")) for p in projected]
                    content = ("\n".join(lines) + "\n").encode()
                await self.writer.write(part_key, content)
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
                "format": fmt,
                "fields": exported_columns,
                "cursor_from": run.cursor_from,
                "cursor_to": {"last_id": last_cursor},
                "row_count": total,
                "parts": parts,
                "generated_at": datetime.now(UTC).isoformat(),
            }
            await self.writer.write(manifest_key, json.dumps(manifest, indent=2).encode())
        except AppError:
            raise
        except ParquetSchemaDriftError as exc:
            run.status = "failed"
            run.error = f"PARQUET_SCHEMA_DRIFT: {exc}"[:200]
            run.finished_at = datetime.now(UTC)
            await self.db.flush()
            return run
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


# R183: export cadence parity with sync (manual never auto-runs).
_EXPORT_CADENCE = {"hourly": timedelta(hours=1), "daily": timedelta(days=1)}


async def sweep_scheduled_exports(db: AsyncSession, writer: PartWriter) -> int:
    """Worker cron (R16): scheduled export streams run when their last run is
    older than their cadence (hourly/daily; manual never auto-runs)."""
    from app.integrations.models.export import ExportRun

    streams = (
        (
            await db.execute(
                select(ExportStream).where(
                    ExportStream.enabled.is_(True),
                    ExportStream.schedule.in_(tuple(_EXPORT_CADENCE)),
                )
            )
        )
        .scalars()
        .all()
    )
    ran = 0
    now = datetime.now(UTC)
    for stream in streams:
        cadence = _EXPORT_CADENCE.get(stream.schedule)
        if cadence is None:
            continue
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
            if now - last < cadence:
                continue
        try:
            await WarehouseExportService(db, writer=writer).run_export(stream.org_id, stream.id)
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
                    "application/json"
                    if key.endswith(".json")
                    else "application/vnd.apache.parquet"
                    if key.endswith(".parquet")
                    else "application/x-ndjson"
                ),
            )


def _ulid() -> str:  # kept for import stability in future phases
    return str(ULID())
