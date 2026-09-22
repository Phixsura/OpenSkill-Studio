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
from app.ecosystem.models.mapping import AvailabilityRecord
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

    async def resolve_conflict(
        self,
        kind: str,
        entity_id: str,
        *,
        field: str,
        chosen_value,
        winning_source_id: str | None = None,
        actor_id: str | None = None,
    ) -> dict:
        """Curated arbitration of a source conflict (Snyk curation loop, §14).

        The analyst's decision is stored as a per-field CURATED overlay on the
        entity — the disagreeing observations remain untouched (Part Q: both
        sides stay visible), the overlay records who decided, when, from which
        source. conflicting_observations() marks curated fields.
        """
        allowed_fields = {"license", "sunset_at", "deprecated_at", "version", "api_identifier"}
        if field not in allowed_fields:
            raise AppError(
                "VALIDATION_ERROR", f"Field {field!r} is not conflict-arbitrable", 422
            )
        entity = await self.get(kind, entity_id)
        cleaned = sanitize_text(str(chosen_value), 300)
        curated = dict((entity.extra or {}).get("curated", {}))
        curated[field] = {
            "value": cleaned,
            "source_id": winning_source_id,
            "decided_by": actor_id,
            "decided_at": datetime.now(UTC).isoformat(),
        }
        entity.extra = {**(entity.extra or {}), "curated": curated}
        # Curated license/sunset also update the first-class column when it exists
        if hasattr(entity, field) and field in ("license", "api_identifier"):
            setattr(entity, field, cleaned)
        await self.db.flush()
        return curated[field]

    async def corroboration(self, kind: str, entity_id: str) -> dict:
        """Multi-source corroboration score (StatusGator cross-correlation, §14).

        Trust-weighted count of DISTINCT sources that have observed this
        entity — a fact seen by three official feeds is stronger evidence than
        one unverified blog, and the score says so numerically.
        """
        from app.ecosystem.models.source import EcosystemSource

        await self.get(kind, entity_id)
        weights = {
            "official": 1.0,
            "verified_partner": 0.8,
            "internal": 0.7,
            "community": 0.5,
            "unverified": 0.2,
        }
        rows = await self.db.execute(
            select(
                EcosystemSource.id,
                EcosystemSource.trust_level,
                func.count(EcosystemObservation.id),
                func.max(EcosystemObservation.observed_at),
            )
            .join(EcosystemObservation, EcosystemObservation.source_id == EcosystemSource.id)
            .where(
                EcosystemObservation.canonical_entity_kind == kind,
                EcosystemObservation.canonical_entity_id == entity_id,
            )
            .group_by(EcosystemSource.id, EcosystemSource.trust_level)
        )
        sources = [
            {
                "source_id": source_id,
                "trust_level": trust,
                "observations": count,
                "last_observed_at": last,
            }
            for source_id, trust, count, last in rows
        ]
        score = round(sum(weights.get(s["trust_level"], 0.2) for s in sources), 2)
        return {
            "distinct_sources": len(sources),
            "trust_weighted_score": score,
            "human_verified_any": bool(
                await self.db.scalar(
                    select(EcosystemObservation.id)
                    .where(
                        EcosystemObservation.canonical_entity_kind == kind,
                        EcosystemObservation.canonical_entity_id == entity_id,
                        EcosystemObservation.human_verified.is_(True),
                    )
                    .limit(1)
                )
            ),
            "sources": sources,
        }

    async def scorecard(self, kind: str, entity_id: str) -> dict:
        """Backstage-style scorecard: independent PASS/WARN/FAIL checks, each
        with its raw evidence. Deliberately NOT collapsed into one magic
        number — the grade is the count of passing checks over applicable
        checks, and every check shows why."""
        from datetime import UTC, datetime, timedelta

        from app.ecosystem.services.benchmark import latest_completed_run
        from app.ecosystem.services.pricing import AvailabilityService, PricingService

        entity = await self.get(kind, entity_id)
        now = datetime.now(UTC)
        checks: list[dict] = []

        def check(key: str, status: str, evidence: dict) -> None:
            checks.append({"check": key, "status": status, "evidence": evidence})

        # 1. Lifecycle: verified/active is healthy, deprecated/sunset fails
        lc = entity.lifecycle_status
        check(
            "lifecycle",
            "pass" if lc in ("verified", "active") else
            "fail" if lc in ("deprecated", "sunset", "blocked") else "warn",
            {"lifecycle_status": lc},
        )
        # 2. Corroboration: >=2 distinct sources or human verification
        corr = await self.corroboration(kind, entity_id)
        check(
            "corroboration",
            "pass" if corr["distinct_sources"] >= 2 or corr["human_verified_any"] else
            "warn" if corr["distinct_sources"] == 1 else "fail",
            {
                "distinct_sources": corr["distinct_sources"],
                "trust_weighted_score": corr["trust_weighted_score"],
                "human_verified_any": corr["human_verified_any"],
            },
        )
        # 3. Freshness: observed within 30d passes, 90d warns, older fails
        last_seen = max(
            (s2["last_observed_at"] for s2 in corr["sources"] if s2["last_observed_at"]),
            default=None,
        )
        if last_seen is not None and last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=UTC)
        age_days = (now - last_seen).days if last_seen else None
        check(
            "freshness",
            "fail" if age_days is None or age_days > 90 else
            "warn" if age_days > 30 else "pass",
            {"last_observed_at": last_seen.isoformat() if last_seen else None,
             "age_days": age_days},
        )
        # 4. Availability: recent operational probe passes; degraded fails;
        #    never probed = not-applicable (honest unknown, not a failure)
        uptime = await AvailabilityService(self.db).uptime(
            entity_kind=kind, entity_id=entity_id, days=30
        )
        if uptime["current_status"] == "unknown":
            check("availability", "n/a", {"reason": "never probed"})
        else:
            check(
                "availability",
                "pass" if uptime["current_status"] == "operational" else "fail",
                {"current_status": uptime["current_status"],
                 "uptime_pct": uptime["uptime_pct"],
                 "incidents_30d": uptime["incidents"]},
            )
        # 5. Benchmark coverage: a completed run in 90d passes; ever = warn
        run = await latest_completed_run(self.db, kind, entity_id)
        if run is None:
            check("benchmark", "n/a", {"reason": "never benchmarked"})
        else:
            fin = run.finished_at
            if fin is not None and fin.tzinfo is None:
                fin = fin.replace(tzinfo=UTC)
            stale = fin is None or (now - fin) > timedelta(days=90)
            check(
                "benchmark",
                "warn" if stale else "pass",
                {"run_id": run.id,
                 "finished_at": fin.isoformat() if fin else None},
            )
        # 6. Pricing: any non-rejected price known; approved passes
        prices = await PricingService(self.db).latest_prices(kind, entity_id)
        if not prices:
            check("pricing", "n/a", {"reason": "no observed prices"})
        else:
            check(
                "pricing",
                "pass" if any(p2["approved"] for p2 in prices.values()) else "warn",
                {"units": sorted(prices),
                 "any_approved": any(p2["approved"] for p2 in prices.values())},
            )
        applicable = [c for c in checks if c["status"] != "n/a"]
        passing = sum(1 for c in applicable if c["status"] == "pass")
        failing = sum(1 for c in applicable if c["status"] == "fail")
        return {
            "entity_kind": kind,
            "entity_id": entity_id,
            "canonical_name": entity.canonical_name,
            "grade": "healthy" if failing == 0 and passing == len(applicable)
            else "failing" if failing > 0 else "attention",
            "passing": passing,
            "applicable": len(applicable),
            "checks": checks,
        }

    async def global_search(self, q: str, *, limit_per_kind: int = 3) -> list[dict]:
        """One search box across all seven catalog kinds (HF posture, §14).

        Indexed trigram similarity per kind; Python fallback keeps unit
        contexts working without pg_trgm.
        """
        from sqlalchemy import text as sql_text

        from app.ecosystem.services.resolution import _KIND_TABLES, normalize_name

        cleaned = normalize_name(q) or (sanitize_text(q, 100) or "").lower()
        if not cleaned:
            return []
        results: list[dict] = []
        for kind, table in _KIND_TABLES.items():
            try:
                rows = await self.db.execute(
                    sql_text(
                        f"SELECT id, canonical_name, lifecycle_status, "  # noqa: S608 — table from fixed map
                        f"similarity(lower(canonical_name), :q) AS score "
                        f"FROM {table} WHERE lower(canonical_name) % :q "
                        f"ORDER BY score DESC LIMIT :n"
                    ),
                    {"q": cleaned, "n": limit_per_kind},
                )
                for row in rows:
                    results.append(
                        {
                            "kind": kind,
                            "id": row.id,
                            "canonical_name": row.canonical_name,
                            "lifecycle_status": row.lifecycle_status,
                            "score": round(float(row.score), 3),
                        }
                    )
            except Exception:  # noqa: BLE001 — pg_trgm unavailable
                model = CATALOG_KIND_TO_MODEL[kind]
                rows = await self.db.scalars(
                    select(model).where(model.canonical_name.ilike(f"%{cleaned}%")).limit(
                        limit_per_kind
                    )
                )
                for entity in rows:
                    results.append(
                        {
                            "kind": kind,
                            "id": entity.id,
                            "canonical_name": entity.canonical_name,
                            "lifecycle_status": entity.lifecycle_status,
                            "score": 0.5,
                        }
                    )
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:20]

    async def compare_entities(self, kind: str, entity_ids: list[str]) -> list[dict]:
        """Side-by-side comparison (Artificial-Analysis style): canonical facts,
        latest per-unit pricing, latest availability status, latest benchmark
        dimension scores. Missing entities 404 (uniform, no existence oracle
        difference between 1 and N)."""
        from app.ecosystem.services.benchmark import latest_completed_run
        from app.ecosystem.services.pricing import PricingService

        if not (2 <= len(entity_ids) <= 6):
            raise AppError("VALIDATION_ERROR", "Compare 2-6 entities", 422)
        if len(set(entity_ids)) != len(entity_ids):
            raise AppError("VALIDATION_ERROR", "Duplicate entity ids", 422)
        pricing = PricingService(self.db)
        out = []
        for entity_id in entity_ids:
            entity = await self.get(kind, entity_id)  # 404s uniformly
            run = await latest_completed_run(self.db, kind, entity_id)
            status_row = await self.db.scalar(
                select(AvailabilityRecord)
                .where(
                    AvailabilityRecord.entity_kind == kind,
                    AvailabilityRecord.entity_id == entity_id,
                    AvailabilityRecord.record_type == "status",
                )
                .order_by(AvailabilityRecord.observed_at.desc())
                .limit(1)
            )
            out.append(
                {
                    "entity_kind": kind,
                    "entity_id": entity_id,
                    "canonical_name": entity.canonical_name,
                    "lifecycle_status": entity.lifecycle_status,
                    "metadata": getattr(entity, "metadata_", None) or {},
                    "prices": await pricing.latest_prices(kind, entity_id),
                    "availability_status": (status_row.value if status_row else None),
                    "benchmark": (
                        {
                            "run_id": run.id,
                            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                            "dimension_scores": run.dimension_scores or {},
                        }
                        if run
                        else None
                    ),
                }
            )
        return out

    async def find_duplicates(
        self, kind: str, *, threshold: float = 0.55, limit: int = 50
    ) -> list[dict]:
        """Backstage/deps.dev dedup bar: trigram self-join surfacing entity
        PAIRS whose canonical names are suspiciously similar. Suggestion only —
        merging stays the operator's explicit, audited action. Retired
        entities are excluded; each pair reported once (a.id < b.id)."""
        from sqlalchemy import text as sql_text

        from app.ecosystem.services.resolution import _KIND_TABLES

        table = _KIND_TABLES.get(kind)
        if table is None:
            raise AppError("VALIDATION_ERROR", f"Unknown entity kind: {kind}", 422)
        if not (0.3 <= threshold <= 1.0):
            raise AppError("VALIDATION_ERROR", "threshold must be 0.3-1.0", 422)
        try:
            rows = await self.db.execute(
                sql_text(
                    f"SELECT a.id AS id_a, a.canonical_name AS name_a, "  # noqa: S608 — table from fixed map
                    f"a.lifecycle_status AS status_a, "
                    f"b.id AS id_b, b.canonical_name AS name_b, "
                    f"b.lifecycle_status AS status_b, "
                    f"similarity(lower(a.canonical_name), lower(b.canonical_name)) AS score "
                    f"FROM {table} a JOIN {table} b ON a.id < b.id "
                    f"WHERE a.lifecycle_status != 'retired' "
                    f"AND b.lifecycle_status != 'retired' "
                    f"AND similarity(lower(a.canonical_name), lower(b.canonical_name)) >= :t "
                    f"ORDER BY score DESC LIMIT :n"
                ),
                {"t": threshold, "n": limit},
            )
        except Exception:  # noqa: BLE001 — pg_trgm unavailable: no suggestions, never an error
            return []
        return [
            {
                "kind": kind,
                "a": {"id": r.id_a, "canonical_name": r.name_a, "lifecycle_status": r.status_a},
                "b": {"id": r.id_b, "canonical_name": r.name_b, "lifecycle_status": r.status_b},
                "similarity": round(float(r.score), 3),
            }
            for r in rows
        ]

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
        # Concurrent-merge fence: lock BOTH rows in a deterministic order (by
        # id — no deadly embrace with a concurrent B→A merge), then re-check
        # inside the lock that neither side was already retired by a racing
        # merge. Without this, A→B racing B→A retires both entities.
        for entity in sorted((source, target), key=lambda e: e.id):
            await self.db.refresh(entity, with_for_update=True)
        if source.lifecycle_status == "retired" or target.lifecycle_status == "retired":
            raise AppError(
                "ECO_INVALID_TRANSITION", "Entity already merged/retired", 409
            )
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

        # Watchers follow the survivor: re-point watch items so a user who
        # watched the duplicate keeps receiving the survivor's change events.
        # Lists already watching the survivor drop the now-duplicate item.
        from app.ecosystem.models.replacement import WatchItem

        src_items = list(
            await self.db.scalars(select(WatchItem).where(WatchItem.target_id == source_id))
        )
        moved["watch_items"] = 0
        for item in src_items:
            duplicate = await self.db.scalar(
                select(WatchItem.id).where(
                    WatchItem.watchlist_id == item.watchlist_id,
                    WatchItem.target_id == target_id,
                )
            )
            if duplicate:
                await self.db.delete(item)
            else:
                item.target_id = target_id
                moved["watch_items"] += 1

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
                entity = await self.get(kind, entity_id)
                curated = ((entity.extra or {}).get("curated") or {}).get(field)
                conflicts.append({"field": field, "values": values, "curated": curated})
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
        # Row lock: concurrent transitions serialize so the state machine
        # always validates against the CURRENT status, and the transition
        # audit log matches the entity's actual path.
        if reason is not None and reason not in DEPRECATION_REASONS:
            raise AppError("VALIDATION_ERROR", f"Unknown reason: {reason}", 422)
        entity = await CatalogService(self.db).get(kind, entity_id)
        await self.db.refresh(entity, with_for_update=True)
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
