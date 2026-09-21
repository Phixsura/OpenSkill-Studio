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

    async def merge_entities(
        self, kind: str, source_id: str, target_id: str, *, actor_id: str | None = None
    ) -> dict:
        """Merge duplicate canonical entities (§13 — registry dedupe tooling).

        Everything referencing the duplicate is re-pointed at the survivor:
        observations, aliases (unique-conflict rows dropped — survivor's alias
        wins), capability mappings (higher evidence level wins on conflict),
        dependency edges (both directions; duplicate edges dropped), price
        observations, availability records. The duplicate is retired with an
        audited lifecycle transition and a `supersedes` replacement edge —
        NOTHING is deleted except now-redundant duplicate rows, and the
        merge is fully reconstructible from the audit trail.
        """
        if source_id == target_id:
            raise AppError("VALIDATION_ERROR", "Cannot merge an entity into itself", 422)
        source = await self.get(kind, source_id)
        target = await self.get(kind, target_id)
        from sqlalchemy import update

        from app.ecosystem.models.catalog import EntityAlias
        from app.ecosystem.models.graph import DependencyEdge
        from app.ecosystem.models.mapping import (
            EVIDENCE_RANK,
            AvailabilityRecord,
            CapabilityMapping,
            PriceObservation,
        )

        moved = {"observations": 0, "aliases": 0, "mappings": 0, "edges": 0, "prices": 0}

        result = await self.db.execute(
            update(EcosystemObservation)
            .where(
                EcosystemObservation.canonical_entity_kind == kind,
                EcosystemObservation.canonical_entity_id == source_id,
            )
            .values(canonical_entity_id=target_id)
        )
        moved["observations"] = result.rowcount or 0

        # Aliases: unique on (kind, alias, alias_type) — survivor's row wins
        aliases = await self.db.scalars(
            select(EntityAlias).where(
                EntityAlias.entity_kind == kind, EntityAlias.entity_id == source_id
            )
        )
        for alias in list(aliases):
            duplicate = await self.db.scalar(
                select(EntityAlias).where(
                    EntityAlias.entity_kind == kind,
                    EntityAlias.alias == alias.alias,
                    EntityAlias.alias_type == alias.alias_type,
                    EntityAlias.entity_id == target_id,
                )
            )
            if duplicate:
                await self.db.delete(alias)
            else:
                alias.entity_id = target_id
                moved["aliases"] += 1

        # Capability mappings: unique per capability_key — higher evidence wins
        mappings = await self.db.scalars(
            select(CapabilityMapping).where(
                CapabilityMapping.entity_kind == kind,
                CapabilityMapping.entity_id == source_id,
            )
        )
        for mapping in list(mappings):
            existing = await self.db.scalar(
                select(CapabilityMapping).where(
                    CapabilityMapping.entity_kind == kind,
                    CapabilityMapping.entity_id == target_id,
                    CapabilityMapping.capability_key == mapping.capability_key,
                )
            )
            if existing:
                if EVIDENCE_RANK[mapping.evidence_level] > EVIDENCE_RANK[existing.evidence_level]:
                    existing.evidence_level = mapping.evidence_level
                    existing.io_spec = mapping.io_spec
                    existing.confidence = mapping.confidence
                await self.db.delete(mapping)
            else:
                mapping.entity_id = target_id
                moved["mappings"] += 1

        # Dependency edges, both directions; drop rows that become duplicates
        for column_kind, column_id in (
            (DependencyEdge.to_kind, DependencyEdge.to_id),
            (DependencyEdge.from_kind, DependencyEdge.from_id),
        ):
            edges = await self.db.scalars(
                select(DependencyEdge).where(column_kind == kind, column_id == source_id)
            )
            for edge in list(edges):
                is_target_side = column_id is DependencyEdge.to_id
                new_from = (edge.from_kind, edge.from_id) if is_target_side else (kind, target_id)
                new_to = (kind, target_id) if is_target_side else (edge.to_kind, edge.to_id)
                duplicate = await self.db.scalar(
                    select(DependencyEdge).where(
                        DependencyEdge.from_kind == new_from[0],
                        DependencyEdge.from_id == new_from[1],
                        DependencyEdge.to_kind == new_to[0],
                        DependencyEdge.to_id == new_to[1],
                        DependencyEdge.constraint_type == edge.constraint_type,
                    )
                )
                if duplicate:
                    await self.db.delete(edge)
                else:
                    if is_target_side:
                        edge.to_id = target_id
                    else:
                        edge.from_id = target_id
                    moved["edges"] += 1

        result = await self.db.execute(
            update(PriceObservation)
            .where(
                PriceObservation.entity_kind == kind,
                PriceObservation.entity_id == source_id,
            )
            .values(entity_id=target_id)
        )
        moved["prices"] = result.rowcount or 0
        await self.db.execute(
            update(AvailabilityRecord)
            .where(
                AvailabilityRecord.entity_kind == kind,
                AvailabilityRecord.entity_id == source_id,
            )
            .values(entity_id=target_id)
        )

        # Merge alias/external_id lists onto the survivor
        target.aliases = sorted(
            {*(target.aliases or []), *(source.aliases or []), source.canonical_name}
        )
        target.external_ids = {**(source.external_ids or {}), **(target.external_ids or {})}

        # Audit: retire the duplicate + record succession
        from app.ecosystem.models.replacement import ReplacementEdge

        self.db.add(
            LifecycleTransition(
                entity_kind=kind,
                entity_id=source_id,
                from_status=source.lifecycle_status,
                to_status="retired",
                reason="manual_decision",
                note=f"Merged into {target_id}",
                actor_id=actor_id,
            )
        )
        source.lifecycle_status = "retired"
        self.db.add(
            ReplacementEdge(
                from_kind=kind,
                from_id=source_id,
                to_kind=kind,
                to_id=target_id,
                edge_type="supersedes",
                rationale=f"Canonical entity merge (duplicate of {target_id})",
                created_by=actor_id,
            )
        )
        await self.db.flush()
        return {"merged_into": target_id, "retired": source_id, "moved": moved}

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
