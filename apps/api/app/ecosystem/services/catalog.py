"""Canonical catalog CRUD + lifecycle governance (ADR-016 Parts C, L)."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.catalog import (
    CATALOG_KIND_TO_MODEL,
    DEPRECATION_REASONS,
    LIFECYCLE_STATUSES,
    LIFECYCLE_TRANSITIONS,
    LifecycleTransition,
)
from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.security import sanitize_text
from app.exceptions import AppError


def _model_for(kind: str):
    model = CATALOG_KIND_TO_MODEL.get(kind)
    if model is None:
        raise AppError("VALIDATION_ERROR", f"Unknown entity kind: {kind}", 422)
    return model


class CatalogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, kind: str, entity_id: str):
        entity = await self.db.get(_model_for(kind), entity_id)
        if entity is None:
            raise AppError("NOT_FOUND", "Entity not found", 404)
        return entity

    async def list_entities(
        self,
        kind: str,
        *,
        lifecycle_status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        model = _model_for(kind)
        query = select(model)
        if lifecycle_status:
            query = query.where(model.lifecycle_status == lifecycle_status)
        if search:
            cleaned = sanitize_text(search, 200) or ""
            query = query.where(model.canonical_name.ilike(f"%{cleaned}%"))
        total = await self.db.scalar(select(func.count()).select_from(query.subquery()))
        rows = await self.db.scalars(
            query.order_by(model.created_at.desc()).limit(limit).offset(offset)
        )
        return list(rows), total or 0

    async def update(self, kind: str, entity_id: str, updates: dict):
        entity = await self.get(kind, entity_id)
        # lifecycle_status changes must go through transition() — never PATCH
        allowed = {"canonical_name", "description", "aliases", "external_ids"}
        for key, value in updates.items():
            if key in allowed:
                setattr(entity, key, value)
        await self.db.flush()
        return entity

    async def conflicting_observations(self, kind: str, entity_id: str) -> list[dict]:
        """Surface disagreeing sources for one entity (Part Q: never merge truth)."""
        rows = await self.db.scalars(
            select(EcosystemObservation)
            .where(
                EcosystemObservation.canonical_entity_kind == kind,
                EcosystemObservation.canonical_entity_id == entity_id,
                EcosystemObservation.superseded_by_id.is_(None),
            )
            .order_by(EcosystemObservation.observed_at.desc())
            .limit(200)
        )
        observations = list(rows)
        # Group latest observation per source; disagreements on tracked fields
        latest_per_source: dict[str, EcosystemObservation] = {}
        for obs in observations:
            latest_per_source.setdefault(obs.source_id, obs)
        conflicts: list[dict] = []
        tracked = ("license", "sunset_at", "deprecated_at", "version", "api_identifier")
        sources = list(latest_per_source.values())
        for field in tracked:
            values: dict[str, list[str]] = {}
            for obs in sources:
                val = (obs.normalized or {}).get(field)
                if val is not None:
                    values.setdefault(str(val), []).append(obs.source_id)
            if len(values) > 1:
                conflicts.append({"field": field, "values": values})
        return conflicts


class LifecycleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def transition(
        self,
        kind: str,
        entity_id: str,
        *,
        to_status: str,
        reason: str | None = None,
        note: str | None = None,
        actor_id: str | None = None,
    ):
        """Apply a validated lifecycle transition (Part L state machine)."""
        if to_status not in LIFECYCLE_STATUSES:
            raise AppError("VALIDATION_ERROR", f"Unknown lifecycle status: {to_status}", 422)
        if reason is not None and reason not in DEPRECATION_REASONS:
            raise AppError("VALIDATION_ERROR", f"Unknown reason: {reason}", 422)
        entity = await CatalogService(self.db).get(kind, entity_id)
        from_status = entity.lifecycle_status
        if to_status not in LIFECYCLE_TRANSITIONS.get(from_status, frozenset()):
            raise AppError(
                "ECO_INVALID_TRANSITION",
                f"Cannot transition {from_status} -> {to_status}",
                409,
            )
        if to_status == "deprecated" and reason is None:
            raise AppError("VALIDATION_ERROR", "Deprecation requires a reason", 422)
        entity.lifecycle_status = to_status
        self.db.add(
            LifecycleTransition(
                entity_kind=kind,
                entity_id=entity_id,
                from_status=from_status,
                to_status=to_status,
                reason=reason,
                note=sanitize_text(note, 2000),
                actor_id=actor_id,
            )
        )
        await self.db.flush()
        return entity

    async def history(self, kind: str, entity_id: str) -> list[LifecycleTransition]:
        rows = await self.db.scalars(
            select(LifecycleTransition)
            .where(
                LifecycleTransition.entity_kind == kind,
                LifecycleTransition.entity_id == entity_id,
            )
            .order_by(LifecycleTransition.created_at)
        )
        return list(rows)

    async def upcoming_sunsets(self, *, within_days: int = 90) -> list[dict]:
        """Deprecation calendar feed (Part P)."""
        from datetime import timedelta

        from app.ecosystem.models.catalog import ModelVersion

        horizon = datetime.now(UTC) + timedelta(days=within_days)
        rows = await self.db.scalars(
            select(ModelVersion)
            .where(ModelVersion.sunset_at.isnot(None), ModelVersion.sunset_at <= horizon)
            .order_by(ModelVersion.sunset_at)
            .limit(200)
        )
        return [
            {
                "entity_kind": "model_version",
                "entity_id": mv.id,
                "name": mv.canonical_name,
                "sunset_at": mv.sunset_at,
                "lifecycle_status": mv.lifecycle_status,
            }
            for mv in rows
        ]
