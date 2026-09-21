"""Replacement & migration intelligence (ADR-016 Part J).

Two-phase, mirroring the matching engine (ADR-012): hard constraints first
(typed I/O compatibility, license, lifecycle), then soft scoring. Hard
incompatibilities are NEVER hidden by soft ranking — incompatible candidates
are returned in a separate list. Recommendations are explainable and only a
human can approve one.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.catalog import CATALOG_KIND_TO_MODEL, ModelVersion
from app.ecosystem.models.graph import TelemetrySnapshot
from app.ecosystem.models.mapping import EVIDENCE_RANK, CapabilityMapping
from app.ecosystem.models.replacement import (
    DEFAULT_REPLACEMENT_WEIGHTS,
    REPLACEMENT_EDGE_TYPES,
    ReplacementCandidate,
    ReplacementEdge,
)
from app.ecosystem.services.benchmark import latest_dimension_scores
from app.exceptions import AppError


def _io_types(io_spec: dict, side: str) -> set[str]:
    out = set()
    for item in (io_spec or {}).get(side, []):
        if isinstance(item, dict) and isinstance(item.get("type"), str):
            out.add(item["type"])
        elif isinstance(item, str):
            out.add(item)
    return out


def check_hard_compatibility(
    deprecated_maps: list[CapabilityMapping],
    candidate_maps: list[CapabilityMapping],
    candidate_entity,
) -> list[dict]:
    """Return the list of hard failures ([] = compatible)."""
    failures: list[dict] = []
    dep_caps = {m.capability_key for m in deprecated_maps}
    cand_caps = {m.capability_key for m in candidate_maps}
    missing = dep_caps - cand_caps
    if missing:
        failures.append(
            {"code": "CAPABILITY_MISSING", "detail": f"Candidate lacks: {sorted(missing)}"}
        )
    # Typed I/O: candidate must accept every input type and produce every
    # output type of the deprecated entity, per shared capability
    cand_by_cap = {m.capability_key: m for m in candidate_maps}
    for dep_map in deprecated_maps:
        cand_map = cand_by_cap.get(dep_map.capability_key)
        if cand_map is None:
            continue  # already covered by CAPABILITY_MISSING
        dep_in, cand_in = _io_types(dep_map.io_spec, "inputs"), _io_types(cand_map.io_spec, "inputs")
        dep_out, cand_out = _io_types(dep_map.io_spec, "outputs"), _io_types(
            cand_map.io_spec, "outputs"
        )
        if dep_in and cand_in and not dep_in <= cand_in:
            failures.append(
                {
                    "code": "IO_TYPE_MISMATCH",
                    "detail": f"{dep_map.capability_key}: inputs {sorted(dep_in - cand_in)} unsupported",
                }
            )
        if dep_out and cand_out and not dep_out <= cand_out:
            failures.append(
                {
                    "code": "IO_TYPE_MISMATCH",
                    "detail": f"{dep_map.capability_key}: outputs {sorted(dep_out - cand_out)} missing",
                }
            )
    # Lifecycle: blocked/retired/deprecated candidates are never compatible
    lifecycle = getattr(candidate_entity, "lifecycle_status", None)
    if lifecycle in ("blocked", "retired", "deprecated"):
        failures.append(
            {"code": "LIFECYCLE_INCOMPATIBLE", "detail": f"Candidate is {lifecycle}"}
        )
    # License: commercial use must not be explicitly disallowed
    if getattr(candidate_entity, "commercial_use_allowed", None) is False:
        failures.append(
            {"code": "LICENSE_INCOMPATIBLE", "detail": "Commercial use disallowed"}
        )
    return failures


class ReplacementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_candidates(
        self,
        *,
        deprecated_kind: str,
        deprecated_id: str,
        weights: dict | None = None,
        limit: int = 10,
    ) -> tuple[list[ReplacementCandidate], list[ReplacementCandidate]]:
        """Score replacement candidates. Returns (ranked_compatible, incompatible)."""
        if deprecated_kind not in CATALOG_KIND_TO_MODEL:
            raise AppError("VALIDATION_ERROR", f"Unknown entity kind: {deprecated_kind}", 422)
        deprecated = await self.db.get(CATALOG_KIND_TO_MODEL[deprecated_kind], deprecated_id)
        if deprecated is None:
            raise AppError("NOT_FOUND", "Deprecated entity not found", 404)
        weights = self._validate_weights(weights)

        dep_maps = await self._mappings(deprecated_kind, deprecated_id)
        if not dep_maps:
            raise AppError(
                "VALIDATION_ERROR",
                "Deprecated entity has no capability mappings — map capabilities first",
                422,
            )
        dep_caps = {m.capability_key for m in dep_maps}

        # Candidate pool: same-kind entities sharing at least one capability
        candidate_ids = await self.db.scalars(
            select(CapabilityMapping.entity_id)
            .where(
                CapabilityMapping.entity_kind == deprecated_kind,
                CapabilityMapping.capability_key.in_(dep_caps),
                CapabilityMapping.entity_id != deprecated_id,
            )
            .distinct()
        )
        compatible: list[ReplacementCandidate] = []
        incompatible: list[ReplacementCandidate] = []
        dep_scores = await latest_dimension_scores(self.db, deprecated_kind, deprecated_id)
        for cand_id in candidate_ids:
            entity = await self.db.get(CATALOG_KIND_TO_MODEL[deprecated_kind], cand_id)
            if entity is None:
                continue
            cand_maps = await self._mappings(deprecated_kind, cand_id)
            failures = check_hard_compatibility(dep_maps, cand_maps, entity)
            breakdown, explanation = await self._soft_scores(
                deprecated_kind, cand_id, dep_maps, cand_maps, entity, dep_scores
            )
            score = round(sum(breakdown[k] * weights[k] for k in weights), 4)
            candidate = ReplacementCandidate(
                deprecated_kind=deprecated_kind,
                deprecated_id=deprecated_id,
                candidate_kind=deprecated_kind,
                candidate_id=cand_id,
                score=score if not failures else 0,
                hard_compatible=not failures,
                hard_failures=failures,
                score_breakdown=breakdown,
                explanation=explanation,
                status="proposed",
            )
            self.db.add(candidate)
            (incompatible if failures else compatible).append(candidate)
        await self.db.flush()
        compatible.sort(key=lambda c: float(c.score), reverse=True)
        return compatible[:limit], incompatible[:limit]

    def _validate_weights(self, weights: dict | None) -> dict:
        merged = dict(DEFAULT_REPLACEMENT_WEIGHTS)
        if weights:
            unknown = set(weights) - set(merged)
            if unknown:
                raise AppError("VALIDATION_ERROR", f"Unknown weight keys: {sorted(unknown)}", 422)
            for key, value in weights.items():
                try:
                    numeric = float(value)
                except (TypeError, ValueError) as exc:
                    raise AppError("VALIDATION_ERROR", f"Weight {key} not numeric", 422) from exc
                if numeric != numeric or not 0 <= numeric <= 1:
                    raise AppError("VALIDATION_ERROR", f"Weight {key} out of [0,1]", 422)
                merged[key] = numeric
        total = sum(merged.values())
        if total <= 0:
            raise AppError("VALIDATION_ERROR", "Weights sum to zero", 422)
        return {k: v / total for k, v in merged.items()}

    async def _mappings(self, kind: str, entity_id: str) -> list[CapabilityMapping]:
        rows = await self.db.scalars(
            select(CapabilityMapping).where(
                CapabilityMapping.entity_kind == kind,
                CapabilityMapping.entity_id == entity_id,
            )
        )
        return list(rows)

    async def _soft_scores(
        self, kind, cand_id, dep_maps, cand_maps, entity, dep_scores
    ) -> tuple[dict, list]:
        """Per-factor 0..1 scores + human-readable explanation lines."""
        breakdown: dict[str, float] = {}
        lines: list[dict] = []

        dep_caps = {m.capability_key for m in dep_maps}
        cand_caps = {m.capability_key for m in cand_maps}
        coverage = len(dep_caps & cand_caps) / len(dep_caps) if dep_caps else 0.0
        breakdown["capability"] = round(coverage, 4)
        lines.append(
            {"factor": "capability", "text": f"Covers {len(dep_caps & cand_caps)}/{len(dep_caps)} required capabilities"}
        )

        # I/O: fraction of shared capabilities with fully compatible typed I/O
        compat_io = 0
        shared = dep_caps & cand_caps
        cand_by_cap = {m.capability_key: m for m in cand_maps}
        for dep_map in dep_maps:
            if dep_map.capability_key not in shared:
                continue
            cand_map = cand_by_cap[dep_map.capability_key]
            din, cin = _io_types(dep_map.io_spec, "inputs"), _io_types(cand_map.io_spec, "inputs")
            dout, cout = _io_types(dep_map.io_spec, "outputs"), _io_types(cand_map.io_spec, "outputs")
            if (not din or din <= cin) and (not dout or dout <= cout):
                compat_io += 1
        breakdown["io"] = round(compat_io / len(shared), 4) if shared else 0.0
        lines.append({"factor": "io", "text": f"Typed I/O compatible on {compat_io}/{len(shared) or 0} shared capabilities"})

        # Evidence strength of the candidate's mappings
        max_rank = max(EVIDENCE_RANK.values())
        evidence = (
            max((EVIDENCE_RANK[m.evidence_level] for m in cand_maps), default=0) / max_rank
        )
        # Benchmark: mean of quality-ish dimensions relative to the deprecated entity
        cand_scores = await latest_dimension_scores(self.db, kind, cand_id)
        breakdown["benchmark"] = self._benchmark_ratio(dep_scores, cand_scores, evidence)
        lines.append({"factor": "benchmark", "text": f"Benchmark evidence score {breakdown['benchmark']:.2f}"})

        # Production reliability from telemetry
        snap = await self.db.scalar(
            select(TelemetrySnapshot)
            .where(
                TelemetrySnapshot.entity_kind == kind,
                TelemetrySnapshot.entity_id == cand_id,
                TelemetrySnapshot.org_id.is_(None),
            )
            .order_by(TelemetrySnapshot.window_end.desc())
            .limit(1)
        )
        reliability = float((snap.metrics or {}).get("success_rate", 0.5)) if snap else 0.5
        breakdown["reliability"] = round(min(max(reliability, 0.0), 1.0), 4)
        lines.append({"factor": "reliability", "text": f"Production success rate {'%.0f%%' % (breakdown['reliability']*100) if snap else 'unknown (neutral 0.5)'}"})

        # Cost/latency from benchmark dimensions when present (lower is better)
        breakdown["cost"] = self._inverse_ratio(dep_scores, cand_scores, "cost_per_case_usd")
        breakdown["latency"] = self._inverse_ratio(dep_scores, cand_scores, "speed_p50_ms")
        lines.append({"factor": "cost", "text": f"Cost score {breakdown['cost']:.2f} (vs incumbent)"})
        lines.append({"factor": "latency", "text": f"Latency score {breakdown['latency']:.2f} (vs incumbent)"})

        breakdown["license"] = 1.0 if getattr(entity, "commercial_use_allowed", None) is not False else 0.0
        breakdown["availability"] = 1.0 if getattr(entity, "lifecycle_status", "") in ("verified", "recommended") else 0.5
        lines.append({"factor": "availability", "text": f"Lifecycle status: {getattr(entity, 'lifecycle_status', 'unknown')}"})

        # Binding compatibility & migration effort: heuristic on api_identifier
        same_family = False
        if isinstance(entity, ModelVersion):
            dep_entity = await self.db.get(ModelVersion, dep_maps[0].entity_id)
            same_family = bool(dep_entity and dep_entity.model_id == entity.model_id)
        breakdown["bindings"] = 1.0 if same_family else 0.6
        breakdown["migration"] = 1.0 if same_family else 0.5
        lines.append(
            {"factor": "migration", "text": "Same model family — drop-in upgrade" if same_family else "Cross-family migration — bindings must be re-verified"}
        )
        return breakdown, lines

    @staticmethod
    def _benchmark_ratio(dep_scores: dict, cand_scores: dict, fallback: float) -> float:
        quality_dims = ("quality", "brief_adherence", "consistency", "commercial_readiness")
        pairs = [
            (dep_scores.get(d), cand_scores.get(d))
            for d in quality_dims
            if dep_scores.get(d) is not None and cand_scores.get(d) is not None
        ]
        if not pairs:
            return round(fallback, 4)
        ratios = [min(c / d, 1.5) / 1.5 if d else 0.5 for d, c in pairs]
        return round(sum(ratios) / len(ratios), 4)

    @staticmethod
    def _inverse_ratio(dep_scores: dict, cand_scores: dict, dim: str) -> float:
        dep, cand = dep_scores.get(dim), cand_scores.get(dim)
        if dep is None or cand is None or dep <= 0:
            return 0.5  # neutral when unknown
        # candidate cheaper/faster than incumbent → >0.5, capped
        return round(min(max(dep / (dep + cand), 0.0), 1.0), 4)

    async def list_candidates(
        self,
        *,
        deprecated_kind: str | None = None,
        deprecated_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[ReplacementCandidate]:
        query = select(ReplacementCandidate)
        if deprecated_kind:
            query = query.where(ReplacementCandidate.deprecated_kind == deprecated_kind)
        if deprecated_id:
            query = query.where(ReplacementCandidate.deprecated_id == deprecated_id)
        if status:
            query = query.where(ReplacementCandidate.status == status)
        rows = await self.db.scalars(
            query.order_by(ReplacementCandidate.score.desc()).limit(limit)
        )
        return list(rows)

    async def decide(
        self, candidate_id: str, *, decision: str, actor_id: str
    ) -> ReplacementCandidate:
        """Human approves/rejects a candidate. Hard-incompatible can't be approved."""
        candidate = await self.db.get(ReplacementCandidate, candidate_id)
        if not candidate:
            raise AppError("NOT_FOUND", "Replacement candidate not found", 404)
        if candidate.status in ("approved", "rejected"):
            raise AppError("ECO_INVALID_TRANSITION", "Candidate already decided", 409)
        if decision == "approve":
            if not candidate.hard_compatible:
                raise AppError(
                    "ECO_HARD_INCOMPATIBLE",
                    "Hard-incompatible candidates can never be approved",
                    409,
                )
            candidate.status = "approved"
        elif decision == "reject":
            candidate.status = "rejected"
        elif decision == "under_review":
            candidate.status = "under_review"
            await self.db.flush()
            return candidate
        else:
            raise AppError("VALIDATION_ERROR", f"Unknown decision: {decision}", 422)
        candidate.decided_by = actor_id
        candidate.decided_at = datetime.now(UTC)
        await self.db.flush()
        return candidate

    async def add_edge(
        self,
        *,
        from_kind: str,
        from_id: str,
        to_kind: str,
        to_id: str,
        edge_type: str,
        rationale: str | None = None,
        created_by: str | None = None,
    ) -> ReplacementEdge:
        if edge_type not in REPLACEMENT_EDGE_TYPES:
            raise AppError("VALIDATION_ERROR", f"Unknown edge type: {edge_type}", 422)
        edge = ReplacementEdge(
            from_kind=from_kind,
            from_id=from_id,
            to_kind=to_kind,
            to_id=to_id,
            edge_type=edge_type,
            rationale=rationale,
            created_by=created_by,
        )
        self.db.add(edge)
        await self.db.flush()
        return edge
