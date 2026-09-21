"""Approved intelligence signals for registry/matching/workforce (Parts N, O).

ONLY entities in lifecycle verified|recommended contribute. Raw unverified
observations never influence production matching. Workforce output is a
planning signal — never an automatic curriculum change.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.catalog import ModelVersion
from app.ecosystem.models.graph import TelemetrySnapshot
from app.ecosystem.models.mapping import EVIDENCE_RANK, CapabilityMapping
from app.ecosystem.models.observation import ChangeEvent
from app.ecosystem.models.replacement import ReplacementEdge

APPROVED_LIFECYCLES = frozenset({"verified", "recommended"})


class SignalsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def matching_signals(self, *, capability_key: str | None = None) -> list[dict]:
        """Per-entity approved signals: benchmark, reliability, deprecation risk.

        Consumers (matching engine) treat these as OPTIONAL soft inputs behind
        a request flag; hard constraints stay in the matching engine.
        """
        query = select(CapabilityMapping)
        if capability_key:
            query = query.where(CapabilityMapping.capability_key == capability_key)
        # Only evidence >= benchmark_verified is signal-worthy
        floor = EVIDENCE_RANK["benchmark_verified"]
        mappings = [
            m
            for m in await self.db.scalars(query)
            if EVIDENCE_RANK.get(m.evidence_level, 0) >= floor
        ]
        signals: list[dict] = []
        for mapping in mappings:
            entity = None
            if mapping.entity_kind == "model_version":
                entity = await self.db.get(ModelVersion, mapping.entity_id)
            if entity is None or entity.lifecycle_status not in APPROVED_LIFECYCLES:
                continue
            snap = await self.db.scalar(
                select(TelemetrySnapshot)
                .where(
                    TelemetrySnapshot.entity_kind == mapping.entity_kind,
                    TelemetrySnapshot.entity_id == mapping.entity_id,
                    TelemetrySnapshot.org_id.is_(None),
                )
                .order_by(TelemetrySnapshot.window_end.desc())
                .limit(1)
            )
            from app.ecosystem.services.benchmark import latest_dimension_scores

            bench = await latest_dimension_scores(self.db, mapping.entity_kind, mapping.entity_id)
            sunset = getattr(entity, "sunset_at", None)
            deprecation_risk = 0.0
            if sunset:
                days = (sunset - datetime.now(UTC)).days
                deprecation_risk = 1.0 if days <= 30 else 0.5 if days <= 90 else 0.2
            signals.append(
                {
                    "entity_kind": mapping.entity_kind,
                    "entity_id": mapping.entity_id,
                    "capability_key": mapping.capability_key,
                    "evidence_level": mapping.evidence_level,
                    "lifecycle_status": entity.lifecycle_status,
                    "benchmark": bench or None,
                    "production_reliability": (snap.metrics or {}).get("success_rate")
                    if snap
                    else None,
                    "cost_efficiency": bench.get("cost_per_case_usd") if bench else None,
                    "deprecation_risk": deprecation_risk,
                    "license_ok": getattr(entity, "commercial_use_allowed", None) is not False,
                }
            )
        return signals

    async def registry_badges(self, *, entity_refs: list[tuple[str, str]]) -> dict:
        """Evidence-backed badges for registry views (Part N)."""
        badges: dict[str, list[str]] = {}
        for kind, entity_id in entity_refs:
            entity_badges: list[str] = []
            mappings = await self.db.scalars(
                select(CapabilityMapping).where(
                    CapabilityMapping.entity_kind == kind,
                    CapabilityMapping.entity_id == entity_id,
                )
            )
            levels = {m.evidence_level for m in mappings}
            if "benchmark_verified" in levels or "human_verified" in levels:
                entity_badges.append("benchmark_verified")
            if "production_verified" in levels:
                entity_badges.append("production_verified")
            update_edge = await self.db.scalar(
                select(ReplacementEdge)
                .where(
                    ReplacementEdge.from_kind == kind,
                    ReplacementEdge.from_id == entity_id,
                    ReplacementEdge.edge_type.in_(
                        ("recommended_replacement", "supersedes")
                    ),
                )
                .limit(1)
            )
            if update_edge:
                entity_badges.append("dependency_update_available")
            if kind == "model_version":
                mv = await self.db.get(ModelVersion, entity_id)
                if mv and mv.sunset_at:
                    entity_badges.append("provider_sunset_risk")
            badges[f"{kind}:{entity_id}"] = entity_badges
        return badges

    async def workforce_signals(self, *, window_days: int = 90) -> list[dict]:
        """Emerging/obsolete capability planning signals (Part O).

        Joins verified ecosystem capabilities with change momentum. Downstream
        consumers combine with talent demand data; output is advisory only.
        """
        since = datetime.now(UTC) - timedelta(days=window_days)
        floor = EVIDENCE_RANK["platform_observed"]
        mappings = [
            m
            for m in await self.db.scalars(select(CapabilityMapping))
            if EVIDENCE_RANK.get(m.evidence_level, 0) >= floor
        ]
        by_capability: dict[str, list[CapabilityMapping]] = {}
        for m in mappings:
            by_capability.setdefault(m.capability_key, []).append(m)
        out: list[dict] = []
        for capability_key, maps in by_capability.items():
            entity_ids = [m.entity_id for m in maps]
            recent_changes = await self.db.scalars(
                select(ChangeEvent)
                .where(
                    ChangeEvent.canonical_entity_id.in_(entity_ids),
                    ChangeEvent.detected_at >= since,
                )
                .limit(500)
            )
            changes = list(recent_changes)
            sunset_count = sum(1 for c in changes if c.severity == "sunset_risk")
            release_momentum = sum(
                1 for c in changes if c.change_type in ("model_version", "lifecycle")
            )
            signal_type = None
            if release_momentum >= 2 and sunset_count == 0:
                signal_type = "emerging_capability"
            elif sunset_count > 0 and sunset_count >= release_momentum:
                signal_type = "possible_obsolescence"
            if signal_type:
                out.append(
                    {
                        "capability_key": capability_key,
                        "signal": signal_type,
                        "verified_entities": len(maps),
                        "recent_changes": len(changes),
                        "sunset_events": sunset_count,
                        "recommendation": "content_development_investigation"
                        if signal_type == "emerging_capability"
                        else "curriculum_review",
                    }
                )
        return out
