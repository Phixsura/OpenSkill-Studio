"""Matching engine orchestrator — S1 → S2 → S3, audited (ADR-012)."""

from dataclasses import dataclass, field

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.matching import FeedbackEvent, MatchingConfig, MatchResult, MatchRun
from app.services.matching import candidates as candidates_mod
from app.services.matching import constraints as constraints_mod
from app.services.matching import scoring as scoring_mod
from app.services.matching.explain import build_explain_tree

log = structlog.get_logger()

ENGINE_VERSION = "1.0.0"
# Cap persisted/returned hard-failure rows per run (excluded_count keeps truth)
MAX_PERSISTED_EXCLUSIONS = 50


@dataclass
class MatchSpec:
    org_id: str
    target_entity_type: str  # workflow_pack | skill_pack | project_template | creator
    requirement: dict = field(default_factory=dict)
    context_type: str = "production"
    requirement_profile_id: str | None = None
    created_by: str | None = None
    limit: int = 20
    explain: bool = False
    # False for composer-internal runs — the user never sees that ranked
    # list, so recording 'shown' rows would pollute position-bias analytics.
    record_impressions: bool = True


class MatchingEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self, spec: MatchSpec) -> tuple[MatchRun, list[MatchResult], list[dict]]:
        """Execute the pipeline. Returns (run, results, explain_trees).

        results includes ranked survivors AND hard-failure rows (rank/score
        NULL). explain_trees aligns with ranked results when spec.explain.
        """
        # Versioned config snapshot (D1)
        config_r = await self.db.execute(
            select(MatchingConfig)
            .where(
                MatchingConfig.target_entity_type == spec.target_entity_type,
                MatchingConfig.is_active.is_(True),
            )
            .order_by(MatchingConfig.version.desc())
            .limit(1)
        )
        config = config_r.scalar_one_or_none()
        if config is None:
            raise AppError(
                "NO_MATCHING_CONFIG",
                f"No active matching config for '{spec.target_entity_type}'",
                500,
            )

        # S1 — eligibility (silent)
        eligible = await candidates_mod.get_candidates(self.db, spec)

        # S2 — hard constraints (visible exclusions)
        survivors, excluded = await constraints_mod.apply_hard_constraints(
            self.db, eligible, spec
        )

        # S3 — deterministic linear scoring
        scored = await scoring_mod.score(self.db, survivors, spec, config)

        # Sort: score desc; tie-break on round(score,4) equal → ULID asc
        scored.sort(key=lambda s: (-round(s["score"], 4), s["entity_id"]))
        scored = scored[: spec.limit]

        thresholds = config.thresholds or {}
        tier_great = float(thresholds.get("tier_great", 0.75))
        tier_good = float(thresholds.get("tier_good", 0.5))

        run = MatchRun(
            org_id=spec.org_id,
            context_type=spec.context_type,
            requirement_profile_id=spec.requirement_profile_id,
            target_entity_type=spec.target_entity_type,
            engine_version=ENGINE_VERSION,
            config_version=config.version,
            candidate_count=len(eligible),
            excluded_count=len(excluded),
            created_by=spec.created_by,
        )
        self.db.add(run)
        await self.db.flush()

        results: list[MatchResult] = []
        explain_trees: list[dict] = []
        for rank, item in enumerate(scored, start=1):
            score_val = item["score"]
            tier = "great" if score_val >= tier_great else ("good" if score_val >= tier_good else "fair")
            result = MatchResult(
                match_run_id=run.id,
                entity_type=spec.target_entity_type,
                entity_id=item["entity_id"],
                rank=rank,
                score=score_val,
                reasons=item["reasons"],
                gaps=item["gaps"],
                hard_failures=[],
                tier=tier,
            )
            self.db.add(result)
            results.append(result)
            if spec.explain:
                explain_trees.append(build_explain_tree(item, config))
            # Impression logging with rank position (R17 — day one).
            # Skipped for composer-internal runs (record_impressions=False).
            if spec.record_impressions:
                self.db.add(
                    FeedbackEvent(
                        org_id=spec.org_id,
                        match_run_id=run.id,
                        entity_type=spec.target_entity_type,
                        entity_id=item["entity_id"],
                        event_type="shown",
                        rank_position=rank,
                        score=score_val,
                        config_version=config.version,
                        created_by=spec.created_by,
                    )
                )

        # Hard failures persisted too — distinguishable from low rank.
        # Bounded: S1 can load the whole registry, so a broad hard constraint
        # would otherwise persist thousands of exclusion rows per run.
        # Newest-first (ULIDs are time-ordered) so the cap keeps the most
        # recently created packs; excluded_count on the run keeps the TRUE total.
        capped = sorted(excluded, key=lambda e: e["entity_id"], reverse=True)
        for exc in capped[:MAX_PERSISTED_EXCLUSIONS]:
            result = MatchResult(
                match_run_id=run.id,
                entity_type=spec.target_entity_type,
                entity_id=exc["entity_id"],
                rank=None,
                score=None,
                reasons=[],
                gaps=[],
                hard_failures=exc["failures"],
                tier=None,
            )
            self.db.add(result)
            results.append(result)

        await self.db.flush()
        log.info(
            "match_run_completed",
            run_id=run.id,
            target=spec.target_entity_type,
            ranked=len(scored),
            excluded=len(excluded),
            config_version=config.version,
        )
        return run, results, explain_trees
