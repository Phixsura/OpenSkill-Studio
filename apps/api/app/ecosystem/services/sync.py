"""Source sync orchestration (ADR-016 Part A/B).

Fetch pipeline: rate limit → robots attestation → SSRF guard → conditional
GET (ETag/Last-Modified) → size-capped read → adapter parse → append-only
observations (idempotent) → typed change detection → circuit breaker.

The HTTP fetcher is injectable so tests never touch the network.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.models.source import (
    CIRCUIT_BREAKER_THRESHOLD,
    EcosystemSource,
    SourceSyncRun,
)
from app.ecosystem.security import EcoSecurityError, sanitize_text, validate_external_url
from app.ecosystem.services.adapters import ADAPTERS, NormalizedItem
from app.ecosystem.services.change_detection import detect_changes
from app.ecosystem.services.resolution import propose_resolution
from app.exceptions import AppError

log = structlog.get_logger()

MAX_FETCH_RETRIES = 3


@dataclass
class FetchResult:
    status_code: int
    body: bytes
    etag: str | None = None
    last_modified: str | None = None


async def _default_fetcher(
    url: str, *, etag: str | None, last_modified: str | None,
    timeout: int, max_bytes: int,
) -> FetchResult:
    """httpx fetch with conditional-GET headers and a streaming size cap."""
    import httpx

    headers = {"User-Agent": "OpenSkillStudio-EcosystemBot/1.0"}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=False, trust_env=False
    ) as client:
        async with client.stream("GET", url, headers=headers) as resp:
            if resp.status_code == 304:
                return FetchResult(304, b"")
            chunks: list[bytes] = []
            total = 0
            async for chunk in resp.aiter_bytes():
                total += len(chunk)
                if total > max_bytes:
                    raise EcoSecurityError(
                        "ECO_PAYLOAD_TOO_LARGE", f"Response exceeds {max_bytes} bytes", 413
                    )
                chunks.append(chunk)
            return FetchResult(
                resp.status_code,
                b"".join(chunks),
                etag=resp.headers.get("ETag"),
                last_modified=resp.headers.get("Last-Modified"),
            )


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    # Guard asyncpg timestamptz overflow at extreme years (R76)
    if parsed.year < 1900 or parsed.year > 3000:
        return None
    return parsed


class SyncService:
    def __init__(self, db: AsyncSession, fetcher=None):
        self.db = db
        self.fetcher = fetcher or _default_fetcher

    async def _check_rate_limit(self, source: EcosystemSource) -> None:
        window_start = datetime.now(UTC) - timedelta(hours=1)
        count = await self.db.scalar(
            select(func.count())
            .select_from(SourceSyncRun)
            .where(
                SourceSyncRun.source_id == source.id,
                SourceSyncRun.started_at >= window_start,
            )
        )
        if (count or 0) >= source.rate_limit_per_hour:
            raise AppError("ECO_RATE_LIMITED", "Source sync rate limit exceeded", 429)

    async def run_sync(
        self, source_id: str, *, raw_payload: bytes | None = None
    ) -> SourceSyncRun:
        """Sync one source. raw_payload bypasses fetch for manual sources."""
        source = await self.db.get(EcosystemSource, source_id)
        if not source:
            raise AppError("NOT_FOUND", "Source not found", 404)
        # §16: row-level mutual exclusion — a second worker syncing the same
        # source concurrently skips immediately (NOWAIT) instead of doing a
        # duplicate fetch. Same-transaction re-entry (tests, retries) is a
        # no-op because the lock is already held by this session.
        try:
            await self.db.execute(
                select(EcosystemSource.id)
                .where(EcosystemSource.id == source_id)
                .with_for_update(nowait=True)
            )
        except Exception as exc:  # noqa: BLE001 — lock held elsewhere
            raise AppError(
                "ECO_SYNC_IN_PROGRESS", "Another worker is syncing this source", 409
            ) from exc
        if source.status == "paused":
            raise AppError("ECO_SOURCE_PAUSED", "Source is paused", 409)
        if source.status == "archived":
            raise AppError("ECO_SOURCE_PAUSED", "Source is archived", 409)
        if not source.robots_compliant:
            raise AppError(
                "ECO_ROBOTS_NOT_ATTESTED",
                "Source lacks robots/ToS compliance attestation",
                422,
            )
        await self._check_rate_limit(source)

        run = SourceSyncRun(
            source_id=source.id, parser_version=source.parser_version, status="running"
        )
        self.db.add(run)
        await self.db.flush()
        source.last_sync_at = datetime.now(UTC)

        try:
            if raw_payload is not None:
                body, status_code, etag, last_modified = raw_payload, 200, None, None
            else:
                if not source.base_url:
                    raise AppError(
                        "VALIDATION_ERROR", "Source has no base_url; supply a payload", 422
                    )
                # SSRF re-check at fetch time (DNS may have changed)
                validate_external_url(source.base_url)
                fetched = await self._fetch_with_retries(source)
                if fetched.status_code == 304:
                    run.status = "not_modified"
                    run.http_status = 304
                    run.finished_at = datetime.now(UTC)
                    source.last_success_at = datetime.now(UTC)
                    source.consecutive_failures = 0
                    await self.db.flush()
                    return run
                if fetched.status_code >= 400:
                    raise AppError(
                        "ECO_FETCH_FAILED", f"Source returned HTTP {fetched.status_code}", 502
                    )
                body = fetched.body
                status_code = fetched.status_code
                etag, last_modified = fetched.etag, fetched.last_modified

            run.http_status = status_code
            run.bytes_fetched = len(body)

            adapter = ADAPTERS.get(source.adapter_key)
            if adapter is None:
                raise AppError("VALIDATION_ERROR", "Source adapter not available", 422)
            items = adapter.parse(body, source.config or {})

            created, changes = await self._ingest(source, run, items)
            run.observations_created = created
            run.changes_detected = changes
            run.status = "success"
            run.finished_at = datetime.now(UTC)
            source.last_success_at = datetime.now(UTC)
            source.consecutive_failures = 0
            if etag:
                source.etag = etag
            if last_modified:
                source.last_modified = last_modified
            await self.db.flush()
            return run
        except (AppError, EcoSecurityError) as exc:
            await self._record_failure(source, run, exc)
            raise
        except Exception as exc:  # noqa: BLE001 — network/parse faults must not 500 silently
            await self._record_failure(source, run, exc)
            raise AppError("ECO_FETCH_FAILED", "Source sync failed", 502) from exc

    async def _fetch_with_retries(self, source: EcosystemSource) -> FetchResult:
        import asyncio

        last_exc: Exception | None = None
        for attempt in range(MAX_FETCH_RETRIES):
            try:
                return await self.fetcher(
                    source.base_url,
                    etag=source.etag,
                    last_modified=source.last_modified,
                    timeout=source.timeout_seconds,
                    max_bytes=source.max_response_bytes,
                )
            except EcoSecurityError:
                raise  # size-cap/SSRF violations are terminal, not retryable
            except Exception as exc:  # noqa: BLE001 — timeouts, connection errors
                last_exc = exc
                if attempt < MAX_FETCH_RETRIES - 1:
                    await asyncio.sleep(2**attempt)  # exponential backoff: 1s, 2s
        raise AppError("ECO_FETCH_FAILED", f"Fetch failed after retries: {last_exc}", 502)

    async def _record_failure(self, source, run, exc) -> None:
        run.status = "failed"
        run.error = sanitize_text(str(exc), 2000)
        run.finished_at = datetime.now(UTC)
        source.consecutive_failures = (source.consecutive_failures or 0) + 1
        if source.consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            source.status = "paused"
            log.warning("eco_source_circuit_breaker", source_id=source.id)
        await self.db.flush()

    async def _ingest(
        self, source: EcosystemSource, run: SourceSyncRun, items: list[NormalizedItem]
    ) -> tuple[int, int]:
        """Insert observations idempotently; detect typed changes for new rows."""
        created = 0
        changes = 0
        for item in items:
            stmt = (
                pg_insert(EcosystemObservation)
                .values(
                    source_id=source.id,
                    sync_run_id=run.id,
                    event_type=item.event_type,
                    entity_kind=item.entity_kind,
                    external_ref=item.external_ref,
                    raw_hash=item.raw_hash,
                    normalized=item.normalized,
                    parser_version=source.parser_version,
                    confidence=item.confidence,
                    provenance_url=item.provenance_url,
                    effective_at=_parse_iso(item.effective_at),
                    extraction_method="manual"
                    if source.adapter_key == "manual"
                    else "structured",
                )
                .on_conflict_do_nothing(constraint="uq_eco_obs_idem")
                .returning(EcosystemObservation.id)
            )
            obs_id = await self.db.scalar(stmt)
            if obs_id is None:
                continue  # duplicate payload — idempotent no-op
            created += 1
            obs = await self.db.get(EcosystemObservation, obs_id)
            changes += await detect_changes(self.db, obs)
            await propose_resolution(self.db, obs, trust_level=source.trust_level)
        return created, changes
