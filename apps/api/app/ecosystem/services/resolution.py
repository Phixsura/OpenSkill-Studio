"""Entity resolution (ADR-016 Part C §3.3, trigram-backed since eco03).

Order: official IDs → deterministic NORMALIZED aliases → indexed pg_trgm
similarity → (optional) LLM suggestion. Only deterministic methods at
confidence >= 0.9 auto-merge; everything else queues for human confirmation.

deps.dev/HF lesson: resolution quality comes from normalization + indexed
similarity, not from fuzzy-matching raw strings in application code. The
Python difflib fallback remains only for DBs without pg_trgm (unit contexts).
"""

import re
from datetime import UTC, datetime
from difflib import SequenceMatcher

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.catalog import (
    AUTO_MERGE_METHODS,
    AUTO_MERGE_MIN_CONFIDENCE,
    CATALOG_KIND_TO_MODEL,
    EntityAlias,
    ResolutionCandidate,
)
from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.security import sanitize_text
from app.exceptions import AppError

SIMILARITY_THRESHOLD = 0.75


def _slugify(value: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "-" for c in value).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out[:200] or "entity"


_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


def normalize_name(value: str | None) -> str | None:
    """Deterministic resolution key: casefold + squash punctuation/whitespace.

    'GPT-Image 2' and 'gpt_image_2' resolve to the same key — the class of
    alias drift that plagues raw-string matching (Lightcast's alias models,
    HF namespace conventions).
    """
    if not isinstance(value, str):
        return None
    normalized = _NORMALIZE_RE.sub(" ", value.casefold()).strip()
    return normalized[:300] or None


# Table names per entity kind for indexed similarity SQL (eco03 trgm indexes)
_KIND_TABLES = {
    "provider": "eco_ai_providers",
    "tool": "eco_ai_tools",
    "model": "eco_ai_models",
    "model_version": "eco_model_versions",
    "workflow": "eco_external_workflows",
    "agent": "eco_external_agents",
    "node_package": "eco_node_packages",
}


async def _find_by_alias(
    db: AsyncSession, entity_kind: str, candidates: list[tuple[str, str]]
) -> tuple[str | None, str | None]:
    """Return (entity_id, method) for the first matching deterministic alias.

    Matches on the NORMALIZED key (exact string as fallback for pre-eco03
    rows), so 'GPT-Image-2' finds an alias registered as 'gpt image 2'.
    """
    for alias_value, alias_type in candidates:
        if not alias_value:
            continue
        normalized = normalize_name(alias_value)
        row = await db.scalar(
            select(EntityAlias).where(
                EntityAlias.entity_kind == entity_kind,
                EntityAlias.alias_type == alias_type,
                (EntityAlias.alias_normalized == normalized)
                if normalized
                else (EntityAlias.alias == alias_value),
            )
        )
        if row is None and normalized:
            row = await db.scalar(
                select(EntityAlias).where(
                    EntityAlias.entity_kind == entity_kind,
                    EntityAlias.alias == alias_value,
                    EntityAlias.alias_type == alias_type,
                )
            )
        if row:
            method = "official_id" if alias_type in ("official_id", "api_identifier") else "alias"
            return row.entity_id, method
    return None, None


async def _similarity_candidate(
    db: AsyncSession, entity_kind: str, name: str
) -> tuple[str | None, float]:
    """Best fuzzy match: indexed pg_trgm over canonical names + normalized
    aliases; Python difflib only as a fallback where pg_trgm is unavailable."""
    model = CATALOG_KIND_TO_MODEL.get(entity_kind)
    table = _KIND_TABLES.get(entity_kind)
    if model is None or not name:
        return None, 0.0
    normalized = normalize_name(name) or name.lower()
    try:
        # Two indexed probes, best of both: canonical names and alias registry
        name_row = (
            await db.execute(
                text(
                    f"SELECT id, similarity(lower(canonical_name), :n) AS sim "  # noqa: S608 — table from fixed map
                    f"FROM {table} WHERE lower(canonical_name) % :n "
                    f"ORDER BY sim DESC LIMIT 1"
                ),
                {"n": normalized},
            )
        ).first()
        alias_row = (
            await db.execute(
                text(
                    "SELECT entity_id, similarity(alias_normalized, :n) AS sim "
                    "FROM eco_entity_aliases "
                    "WHERE entity_kind = :k AND alias_normalized % :n "
                    "ORDER BY sim DESC LIMIT 1"
                ),
                {"n": normalized, "k": entity_kind},
            )
        ).first()
        best_id, best_score = None, 0.0
        if name_row is not None and float(name_row.sim) > best_score:
            best_id, best_score = name_row.id, float(name_row.sim)
        if alias_row is not None and float(alias_row.sim) > best_score:
            best_id, best_score = alias_row.entity_id, float(alias_row.sim)
        return (best_id, round(best_score, 3)) if best_score >= SIMILARITY_THRESHOLD else (
            None,
            round(best_score, 3),
        )
    except Exception:  # noqa: BLE001 — pg_trgm unavailable (non-PG test DB)
        best_id, best_score = None, 0.0
        rows = await db.scalars(select(model).limit(2000))
        lowered = name.lower()
        for row in rows:
            names = [row.canonical_name or ""] + list(row.aliases or [])
            for candidate in names:
                if not isinstance(candidate, str):
                    continue
                score = SequenceMatcher(None, lowered, candidate.lower()).ratio()
                if score > best_score:
                    best_id, best_score = row.id, score
        return (best_id, best_score) if best_score >= SIMILARITY_THRESHOLD else (None, best_score)


async def propose_resolution(
    db: AsyncSession, obs: EcosystemObservation, *, trust_level: str = "unverified"
) -> ResolutionCandidate | None:
    """Create a resolution candidate for a new observation.

    Deterministic high-confidence matches auto-merge (link the observation to
    the canonical entity). Everything else stays pending for a human.
    """
    if not obs.entity_kind or obs.entity_kind not in CATALOG_KIND_TO_MODEL:
        return None
    norm = obs.normalized or {}
    name = sanitize_text(norm.get("name"), 200)
    official_id = sanitize_text(norm.get("official_id"), 300)
    api_identifier = sanitize_text(norm.get("api_identifier"), 300)

    entity_id, method = await _find_by_alias(
        db,
        obs.entity_kind,
        [
            (official_id, "official_id"),
            (api_identifier, "api_identifier"),
            (obs.external_ref, "official_id"),
            (name, "name"),
        ],
    )
    confidence = 1.0 if method == "official_id" else 0.95 if method == "alias" else 0.0

    if entity_id is None and name:
        sim_id, sim_score = await _similarity_candidate(db, obs.entity_kind, name)
        if sim_id:
            entity_id, method, confidence = sim_id, "similarity", round(sim_score, 3)

    candidate = ResolutionCandidate(
        observation_id=obs.id,
        entity_kind=obs.entity_kind,
        candidate_entity_id=entity_id,
        match_method=method or "similarity",
        confidence=confidence,
        proposed_payload=norm,
        status="pending",
    )
    db.add(candidate)
    await db.flush()

    # Auto-merge policy: deterministic method + high confidence ONLY
    if (
        entity_id is not None
        and method in AUTO_MERGE_METHODS
        and confidence >= AUTO_MERGE_MIN_CONFIDENCE
    ):
        candidate.status = "auto_merged"
        candidate.decided_at = datetime.now(UTC)
        obs.canonical_entity_id = entity_id
        obs.canonical_entity_kind = obs.entity_kind
        await db.flush()
    return candidate


class ResolutionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_pending(
        self, *, entity_kind: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[ResolutionCandidate]:
        query = select(ResolutionCandidate).where(ResolutionCandidate.status == "pending")
        if entity_kind:
            query = query.where(ResolutionCandidate.entity_kind == entity_kind)
        rows = await self.db.scalars(
            query.order_by(ResolutionCandidate.created_at).limit(limit).offset(offset)
        )
        return list(rows)

    async def confirm(
        self, candidate_id: str, *, actor_id: str, target_entity_id: str | None = None
    ):
        """Human confirms a merge — or creation of a new canonical entity."""
        candidate = await self.db.get(ResolutionCandidate, candidate_id)
        if not candidate:
            raise AppError("NOT_FOUND", "Resolution candidate not found", 404)
        if candidate.status not in ("pending",):
            raise AppError("ECO_INVALID_TRANSITION", "Candidate already decided", 409)
        entity_id = target_entity_id or candidate.candidate_entity_id
        if entity_id is None:
            entity_id = await self._create_entity(candidate)
        else:
            model = CATALOG_KIND_TO_MODEL[candidate.entity_kind]
            if await self.db.get(model, entity_id) is None:
                raise AppError("NOT_FOUND", "Target canonical entity not found", 404)
        candidate.status = "confirmed"
        candidate.decided_by = actor_id
        candidate.decided_at = datetime.now(UTC)
        obs = await self.db.get(EcosystemObservation, candidate.observation_id)
        if obs:
            obs.canonical_entity_id = entity_id
            obs.canonical_entity_kind = candidate.entity_kind
            await self._register_aliases(candidate, entity_id, obs)
        await self.db.flush()
        return candidate, entity_id

    async def reject(self, candidate_id: str, *, actor_id: str) -> ResolutionCandidate:
        candidate = await self.db.get(ResolutionCandidate, candidate_id)
        if not candidate:
            raise AppError("NOT_FOUND", "Resolution candidate not found", 404)
        if candidate.status != "pending":
            raise AppError("ECO_INVALID_TRANSITION", "Candidate already decided", 409)
        candidate.status = "rejected"
        candidate.decided_by = actor_id
        candidate.decided_at = datetime.now(UTC)
        await self.db.flush()
        return candidate

    async def _create_entity(self, candidate: ResolutionCandidate) -> str:
        """Create a new canonical entity from the proposed payload."""
        model = CATALOG_KIND_TO_MODEL[candidate.entity_kind]
        payload = candidate.proposed_payload or {}
        name = sanitize_text(payload.get("name"), 200) or "unnamed"
        slug = _slugify(name)
        # De-dupe slug (ModelVersion has no slug column — uniqueness is
        # (model_id, version) instead)
        if candidate.entity_kind != "model_version":
            base_slug, i = slug, 1
            while await self.db.scalar(select(model).where(model.slug == slug)):
                i += 1
                slug = f"{base_slug}-{i}"
        kwargs: dict = {
            "canonical_name": name,
            "slug": slug,
            "description": sanitize_text(payload.get("description"), 2000),
            "lifecycle_status": "discovered",
            "first_observed_at": datetime.now(UTC),
        }
        if candidate.entity_kind == "model_version":
            # ModelVersion has no slug/description columns
            kwargs.pop("slug", None)
            kwargs.pop("description", None)
            # A version needs its parent model — resolve or create by name
            from app.ecosystem.models.catalog import AIModel

            model_name = sanitize_text(payload.get("name"), 200) or "unnamed"
            parent = await self.db.scalar(
                select(AIModel).where(AIModel.canonical_name == model_name)
            )
            if parent is None:
                parent = AIModel(
                    canonical_name=model_name,
                    slug=slug + "-family",
                    lifecycle_status="discovered",
                    first_observed_at=datetime.now(UTC),
                )
                self.db.add(parent)
                await self.db.flush()
            kwargs["model_id"] = parent.id
            kwargs["version"] = sanitize_text(payload.get("version"), 100) or "unknown"
            kwargs["api_identifier"] = sanitize_text(payload.get("api_identifier"), 200)
            kwargs["license"] = sanitize_text(payload.get("license"), 100)
            if isinstance(payload.get("limits"), dict):
                kwargs["limits"] = payload["limits"]
            kwargs["canonical_name"] = f"{model_name} {kwargs['version']}"
        entity = model(**kwargs)
        self.db.add(entity)
        await self.db.flush()
        return entity.id

    async def _register_aliases(
        self, candidate: ResolutionCandidate, entity_id: str, obs: EcosystemObservation
    ) -> None:
        """Register deterministic aliases so future observations auto-merge."""
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        payload = candidate.proposed_payload or {}
        pairs = [
            (sanitize_text(payload.get("official_id"), 300), "official_id"),
            (sanitize_text(payload.get("api_identifier"), 300), "api_identifier"),
            (obs.external_ref, "official_id"),
            (sanitize_text(payload.get("name"), 300), "name"),
        ]
        for alias, alias_type in pairs:
            if not alias:
                continue
            await self.db.execute(
                pg_insert(EntityAlias)
                .values(
                    entity_kind=candidate.entity_kind,
                    entity_id=entity_id,
                    alias=alias,
                    alias_normalized=normalize_name(alias),
                    alias_type=alias_type,
                    source_id=obs.source_id,
                )
                .on_conflict_do_nothing(constraint="uq_eco_alias")
            )
