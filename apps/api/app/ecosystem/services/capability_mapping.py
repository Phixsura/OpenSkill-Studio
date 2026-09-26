"""Capability + typed I/O mapping (ADR-016 Part D)."""

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.catalog import CATALOG_KIND_TO_MODEL
from app.ecosystem.models.mapping import EVIDENCE_RANK, CapabilityMapping
from app.exceptions import AppError
from app.models.capability import CapabilityTag


class CapabilityMappingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(
        self,
        *,
        entity_kind: str,
        entity_id: str,
        capability_key: str,
        evidence_level: str = "vendor_claimed",
        io_spec: dict | None = None,
        confidence: float = 0.5,
        source_observation_id: str | None = None,
        actor_id: str | None = None,
        force: bool = False,
        actor_is_admin: bool = False,
    ) -> CapabilityMapping:
        # Depth guard: io_spec is stored verbatim in JSONB — bound it so a
        # single mapping cannot balloon the row (the API is admin-only, but
        # service callers include future import paths)
        if io_spec is not None and len(json.dumps(io_spec, default=str)) > 20_000:
            raise AppError("VALIDATION_ERROR", "io_spec too large (20k max)", 422)
        if evidence_level not in EVIDENCE_RANK:
            raise AppError("VALIDATION_ERROR", f"Unknown evidence level: {evidence_level}", 422)
        if entity_kind not in CATALOG_KIND_TO_MODEL:
            raise AppError("VALIDATION_ERROR", f"Unknown entity kind: {entity_kind}", 422)
        if await self.db.get(CATALOG_KIND_TO_MODEL[entity_kind], entity_id) is None:
            raise AppError("NOT_FOUND", "Entity not found", 404)
        tag = await self.db.scalar(
            select(CapabilityTag).where(CapabilityTag.key == capability_key)
        )
        if tag is None:
            raise AppError("NOT_FOUND", f"Capability {capability_key!r} not found", 404)

        existing = await self.db.scalar(
            select(CapabilityMapping).where(
                CapabilityMapping.entity_kind == entity_kind,
                CapabilityMapping.entity_id == entity_id,
                CapabilityMapping.capability_key == capability_key,
            )
        )
        if existing is None:
            mapping = CapabilityMapping(
                entity_kind=entity_kind,
                entity_id=entity_id,
                capability_key=capability_key,
                evidence_level=evidence_level,
                io_spec=io_spec or {},
                confidence=confidence,
                source_observation_id=source_observation_id,
            )
            if evidence_level == "human_verified":
                mapping.verified_by = actor_id
                mapping.verified_at = datetime.now(UTC)
            self.db.add(mapping)
            await self.db.flush()
            return mapping

        # Evidence order is total: downgrades require force + admin (§3.4)
        if EVIDENCE_RANK[evidence_level] < EVIDENCE_RANK[existing.evidence_level] and not (
            force and actor_is_admin
        ):
            raise AppError(
                "ECO_EVIDENCE_DOWNGRADE",
                f"Cannot downgrade evidence {existing.evidence_level} -> "
                f"{evidence_level} without force+admin",
                409,
            )
        existing.evidence_level = evidence_level
        if io_spec is not None:
            existing.io_spec = io_spec
        existing.confidence = confidence
        if source_observation_id:
            existing.source_observation_id = source_observation_id
        if evidence_level == "human_verified":
            existing.verified_by = actor_id
            existing.verified_at = datetime.now(UTC)
        await self.db.flush()
        return existing

    async def list_for_entity(self, entity_kind: str, entity_id: str) -> list[CapabilityMapping]:
        rows = await self.db.scalars(
            select(CapabilityMapping).where(
                CapabilityMapping.entity_kind == entity_kind,
                CapabilityMapping.entity_id == entity_id,
            )
        )
        return list(rows)

    async def list_for_capability(
        self, capability_key: str, *, min_evidence: str | None = None
    ) -> list[CapabilityMapping]:
        rows = await self.db.scalars(
            select(CapabilityMapping).where(
                CapabilityMapping.capability_key == capability_key
            )
        )
        mappings = list(rows)
        if min_evidence:
            if min_evidence not in EVIDENCE_RANK:
                raise AppError("VALIDATION_ERROR", f"Unknown evidence level: {min_evidence}", 422)
            floor = EVIDENCE_RANK[min_evidence]
            mappings = [m for m in mappings if EVIDENCE_RANK[m.evidence_level] >= floor]
        return mappings
