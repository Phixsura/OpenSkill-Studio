"""External source registry service (ADR-016 Part A)."""

import json
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.source import (
    SOURCE_STATUSES,
    SOURCE_TYPES,
    TRUST_LEVELS,
    EcosystemSource,
    SourceSyncRun,
)
from app.ecosystem.security import validate_external_url
from app.ecosystem.services.adapters import ADAPTERS
from app.exceptions import AppError


def _utcnow() -> datetime:
    return datetime.now(UTC)


class SourceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        name: str,
        source_type: str,
        trust_level: str,
        adapter_key: str,
        base_url: str | None = None,
        config: dict | None = None,
        sync_interval_minutes: int = 1440,
        rate_limit_per_hour: int = 60,
        robots_compliant: bool = True,
        created_by: str | None = None,
    ) -> EcosystemSource:
        if source_type not in SOURCE_TYPES:
            raise AppError("VALIDATION_ERROR", f"Unknown source_type: {source_type}", 422)
        if trust_level not in TRUST_LEVELS:
            raise AppError("VALIDATION_ERROR", f"Unknown trust_level: {trust_level}", 422)
        if adapter_key not in ADAPTERS:
            raise AppError("VALIDATION_ERROR", f"Unknown adapter_key: {adapter_key}", 422)
        if source_type != "manual_analyst" and not base_url:
            raise AppError("VALIDATION_ERROR", "base_url required for non-manual sources", 422)
        if base_url:
            # SSRF guard at registration time; DNS re-checked at every fetch
            validate_external_url(base_url, resolve_dns=False)
        config = config or {}
        # Depth guard (R104): adapter config is stored verbatim in JSONB
        if len(json.dumps(config, default=str)) > 20_000:
            raise AppError("VALIDATION_ERROR", "config too large (20k max)", 422)
        # Credentials must never be stored in source config — field names only
        for key, value in config.items():
            if isinstance(value, str) and any(
                marker in key.lower() for marker in ("secret", "token", "password", "api_key")
            ):
                raise AppError(
                    "VALIDATION_ERROR",
                    f"Config key {key!r} looks like a credential value; "
                    "store credentials by reference, never inline",
                    422,
                )
        existing = await self.db.scalar(
            select(EcosystemSource).where(EcosystemSource.name == name)
        )
        if existing:
            raise AppError("ECO_SOURCE_EXISTS", "A source with this name already exists", 409)
        source = EcosystemSource(
            name=name,
            source_type=source_type,
            trust_level=trust_level,
            adapter_key=adapter_key,
            parser_version=ADAPTERS[adapter_key].version,
            base_url=base_url,
            config=config,
            sync_interval_minutes=sync_interval_minutes,
            rate_limit_per_hour=rate_limit_per_hour,
            robots_compliant=robots_compliant,
            created_by=created_by,
        )
        self.db.add(source)
        await self.db.flush()
        return source

    async def get(self, source_id: str) -> EcosystemSource:
        source = await self.db.get(EcosystemSource, source_id)
        if not source:
            raise AppError("NOT_FOUND", "Source not found", 404)
        return source

    async def list_sources(
        self, *, status: str | None = None, source_type: str | None = None,
        limit: int = 50, offset: int = 0,
    ) -> tuple[list[EcosystemSource], int]:
        query = select(EcosystemSource)
        if status:
            query = query.where(EcosystemSource.status == status)
        if source_type:
            query = query.where(EcosystemSource.source_type == source_type)
        total = await self.db.scalar(
            select(func.count()).select_from(query.subquery())
        )
        rows = await self.db.scalars(
            query.order_by(EcosystemSource.created_at.desc()).limit(limit).offset(offset)
        )
        return list(rows), total or 0

    async def update(self, source_id: str, updates: dict) -> EcosystemSource:
        source = await self.get(source_id)
        allowed = {
            "name",
            "trust_level",
            "adapter_key",
            "base_url",
            "config",
            "sync_interval_minutes",
            "rate_limit_per_hour",
            "max_response_bytes",
            "timeout_seconds",
            "status",
            "robots_compliant",
        }
        for key, value in updates.items():
            if key not in allowed:
                continue
            if key == "trust_level" and value not in TRUST_LEVELS:
                raise AppError("VALIDATION_ERROR", f"Unknown trust_level: {value}", 422)
            if key == "status" and value not in SOURCE_STATUSES:
                raise AppError("VALIDATION_ERROR", f"Unknown status: {value}", 422)
            if key == "base_url" and value:
                validate_external_url(value, resolve_dns=False)
            if key == "adapter_key":
                # §11.5: vendor swap is a config change — re-stamp parser version;
                # historical observations keep their original provenance
                if value not in ADAPTERS:
                    raise AppError("VALIDATION_ERROR", f"Unknown adapter_key: {value}", 422)
                source.parser_version = ADAPTERS[value].version
            setattr(source, key, value)
        # Un-pausing resets the circuit breaker
        if updates.get("status") == "active":
            source.consecutive_failures = 0
        await self.db.flush()
        return source

    async def health(self, source_id: str, *, window_days: int = 7) -> dict:
        """StatusGator-grade source health: success/not-modified/failure rates,
        volume, and the most recent error over a window (§13)."""
        from datetime import UTC, datetime, timedelta

        source = await self.get(source_id)
        window_start = datetime.now(UTC) - timedelta(days=window_days)
        rows = list(
            await self.db.scalars(
                select(SourceSyncRun).where(
                    SourceSyncRun.source_id == source_id,
                    SourceSyncRun.started_at >= window_start,
                )
            )
        )
        total = len(rows)
        by_status: dict[str, int] = {}
        for run in rows:
            by_status[run.status] = by_status.get(run.status, 0) + 1
        succeeded = by_status.get("success", 0) + by_status.get("not_modified", 0)
        last_error_run = max(
            (r for r in rows if r.status == "failed"),
            key=lambda r: r.started_at,
            default=None,
        )
        return {
            "source_id": source_id,
            "status": source.status,
            "window_days": window_days,
            "runs": total,
            "by_status": by_status,
            "success_rate": round(succeeded / total, 4) if total else None,
            "observations_created": sum(r.observations_created for r in rows),
            "changes_detected": sum(r.changes_detected for r in rows),
            "bytes_fetched": sum(r.bytes_fetched for r in rows),
            "consecutive_failures": source.consecutive_failures,
            "last_success_at": source.last_success_at,
            "last_error": last_error_run.error if last_error_run else None,
        }

    async def list_sync_runs(
        self, source_id: str, *, limit: int = 50
    ) -> list[SourceSyncRun]:
        await self.get(source_id)
        rows = await self.db.scalars(
            select(SourceSyncRun)
            .where(SourceSyncRun.source_id == source_id)
            .order_by(SourceSyncRun.started_at.desc())
            .limit(limit)
        )
        return list(rows)
