"""Capability scoring engine — versioned, reproducible, multi-dimensional (ADR-015 D3).

Algorithm v2.0.0 — four scoring dimensions:
  depth    — Bayesian-shrunk expertise score from evidence quality × verification weight
  breadth  — fraction of related capabilities (via CapabilityEdge) that also have evidence
  recency  — freshness of the most recent evidence (Gaussian decay, 180-day half-width)
  velocity — rate of evidence accumulation (last 90 days vs prior 90 days)

  composite score = 0.4×depth + 0.2×breadth + 0.2×recency + 0.2×velocity
"""

from __future__ import annotations

import contextlib
import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.capability import Capability, CapabilityEdge
from app.talent.models.evidence import (
    VERIFICATION_WEIGHTS,
    CapabilityEvidence,
)

SCORING_VERSION = "2.0.0"

# Bayesian shrinkage: k=3 balances single-data-point noise with prior
SHRINKAGE_K = 3
SHRINKAGE_PRIOR = 0.5

# Composite weights
DIMENSION_WEIGHTS = {
    "depth": 0.40,
    "breadth": 0.20,
    "recency": 0.20,
    "velocity": 0.20,
}

# Default level thresholds (overridable per capability family)
DEFAULT_LEVEL_THRESHOLDS: dict[int, dict] = {
    0: {"label": "No evidence", "min_score": 0.00, "min_evidence": 0},
    1: {"label": "Foundation", "min_score": 0.20, "min_evidence": 1},
    2: {"label": "Assisted practice", "min_score": 0.40, "min_evidence": 3},
    3: {"label": "Independent production", "min_score": 0.60, "min_evidence": 5},
    4: {"label": "Commercial delivery", "min_score": 0.75, "min_evidence": 8},
    5: {"label": "Expert / mentor", "min_score": 0.90, "min_evidence": 12},
}

# Verification levels considered "substantial" for min_evidence counting
SUBSTANTIAL_VERIFICATION = frozenset(
    {"employer_verified", "client_verified", "assessment_verified", "instructor_verified", "peer_verified"}
)

# Adjacency edge types for breadth computation
_BREADTH_EDGE_TYPES = frozenset(
    {"related_to", "commonly_paired_with", "specializes", "subsumes"}
)


@dataclass(frozen=True, slots=True)
class CapabilityScore:
    """Derived capability score for a single (user, capability) pair."""

    capability_id: str
    capability_name: str
    level: int
    level_label: str
    score: float
    # Multi-dimensional signals
    depth: float
    breadth: float
    recency: float
    velocity: float
    confidence: float
    evidence_count: int
    substantial_evidence_count: int
    last_verified_at: datetime | None
    verification_mix: dict[str, int]
    scoring_version: str
    computed_at: datetime


def decay_factor(occurred_at: datetime, now: datetime, config: dict | None) -> float:
    """Exponential decay: 2^(-age_days / half_life_days).

    config = {"half_life_days": 365}   # slow decay
    config = {"half_life_days": 90}    # fast decay
    config = None                      # no decay
    """
    if config is None or "half_life_days" not in config:
        return 1.0
    half_life = config["half_life_days"]
    if half_life <= 0:
        return 1.0
    age_days = (now - occurred_at).total_seconds() / 86400
    if age_days < 0:
        return 1.0
    return 2.0 ** (-age_days / half_life)


def compute_score_from_evidence(
    evidence_rows: list[dict],
    decay_config: dict | None,
    now: datetime,
) -> tuple[float, float, int]:
    """Pure depth scoring computation (backward compatible).

    Returns (depth_score, confidence, substantial_count).
    """
    active = []
    for ev in evidence_rows:
        if ev.get("status", "") != "active":
            continue
        if ev.get("expires_at") and ev.get("expires_at", "") < now:
            continue
        active.append(ev)

    if not active:
        return 0.0, 0.0, 0

    effective_scores = []
    for ev in active:
        base = ev.get("score_normalized", "") if ev.get("score_normalized", "") is not None else 0.8
        ver_weight = VERIFICATION_WEIGHTS.get(ev.get("verification_level", ""), 0.5)
        conf = float(ev.get("confidence", 1.0))
        freshness = decay_factor(ev.get("occurred_at", ""), now, decay_config)
        effective = base * ver_weight * conf * freshness
        effective_scores.append(effective)

    n = len(effective_scores)
    raw_mean = sum(effective_scores) / n

    # Bayesian shrinkage
    shrunk = (n / (n + SHRINKAGE_K)) * raw_mean + (SHRINKAGE_K / (n + SHRINKAGE_K)) * SHRINKAGE_PRIOR
    model_confidence = 1.0 - (SHRINKAGE_K / (n + SHRINKAGE_K))

    # Count substantial evidence (for level thresholds)
    substantial = sum(
        1
        for ev in active
        if ev.get("verification_level", "") in SUBSTANTIAL_VERIFICATION
    )

    return round(shrunk, 4), round(model_confidence, 4), substantial


def compute_recency(evidence_rows: list[dict], now: datetime) -> float:
    """Recency signal: Gaussian decay on the most recent active evidence.

    Returns 0-1 where 1 means evidence from today, 0.5 means ~180 days ago.
    """
    active_dates = [
        ev.get("occurred_at", "")
        for ev in evidence_rows
        if ev["status"] == "active" and ev.get("occurred_at")
    ]
    if not active_dates:
        return 0.0
    newest = max(active_dates)
    age_days = (now - newest).total_seconds() / 86400
    if age_days < 0:
        return 1.0
    # Gaussian decay with σ=180 days
    return math.exp(-0.5 * (age_days / 180) ** 2)


def compute_velocity(evidence_rows: list[dict], now: datetime) -> float:
    """Velocity signal: evidence accumulation rate.

    Compares evidence count in last 90 days vs prior 90 days.
    Capped at 2.0, normalized to [0, 1].
    """
    cutoff_recent = now - timedelta(days=90)
    cutoff_prior = now - timedelta(days=180)

    recent_count = 0
    prior_count = 0
    for ev in evidence_rows:
        if ev.get("status", "") != "active":
            continue
        occ = ev.get("occurred_at")
        if not occ:
            continue
        if occ >= cutoff_recent:
            recent_count += 1
        elif occ >= cutoff_prior:
            prior_count += 1

    if prior_count == 0 and recent_count == 0:
        return 0.0
    if prior_count == 0:
        # New learner with only recent evidence — moderate velocity
        return min(recent_count / 3.0, 1.0)
    ratio = recent_count / prior_count
    # Cap at 2.0, normalize to [0, 1]
    return min(ratio / 2.0, 1.0)


def determine_level(
    score: float,
    substantial_count: int,
    level_definitions: dict | None,
) -> tuple[int, str]:
    """Map a score + evidence count to a human-readable level."""
    thresholds = DEFAULT_LEVEL_THRESHOLDS
    if level_definitions:
        # Override with capability-specific definitions
        with contextlib.suppress(ValueError, TypeError):
            thresholds = {int(k): v for k, v in level_definitions.items()}

    best_level = 0
    best_label = thresholds[0]["label"]
    for lvl in sorted(thresholds.keys()):
        t = thresholds[lvl]
        if score >= t["min_score"] and substantial_count >= t["min_evidence"]:
            best_level = lvl
            best_label = t["label"]

    return best_level, best_label


async def compute_capability_profile(
    db: AsyncSession,
    user_id: str,
    capability_ids: list[str] | None = None,
    *,
    use_cache: bool = True,
) -> list[CapabilityScore]:
    """Compute derived capability scores for a user.

    If capability_ids is None, computes for all capabilities the user has
    evidence for.  Results are cached in Redis for 5 minutes when use_cache
    is True and no specific capability_ids filter is applied.
    """
    from app.talent.services.cache import get_cached, profile_cache_key, set_cached

    # Check cache for full profile (skip when filtered to specific capabilities)
    cache_key = profile_cache_key(user_id) if (use_cache and not capability_ids) else None
    if cache_key:
        cached = await get_cached(cache_key)
        if cached is not None:
            return [CapabilityScore(**row) for row in cached]

    now = datetime.now(UTC)

    # Get all active evidence for the user
    q = (
        select(CapabilityEvidence)
        .where(
            CapabilityEvidence.user_id == user_id,
            CapabilityEvidence.status == "active",
        )
    )
    if capability_ids:
        q = q.where(CapabilityEvidence.capability_id.in_(capability_ids))

    result = await db.execute(q)
    evidence_rows = result.scalars().all()

    if not evidence_rows:
        return []

    # Group by capability_id
    by_cap: dict[str, list[dict]] = {}
    for ev in evidence_rows:
        cap_id = ev.capability_id
        if cap_id not in by_cap:
            by_cap[cap_id] = []
        by_cap[cap_id].append({
            "score_normalized": float(ev.score_normalized) if ev.score_normalized is not None else None,
            "verification_level": ev.verification_level,
            "confidence": float(ev.confidence),
            "occurred_at": ev.occurred_at,
            "status": ev.status,
            "expires_at": ev.expires_at,
        })

    # Load capabilities for names and config
    cap_ids = list(by_cap.keys())
    cap_q = select(Capability).where(Capability.id.in_(cap_ids))
    cap_result = await db.execute(cap_q)
    capabilities = {c.id: c for c in cap_result.scalars().all()}

    # Pre-load adjacency edges for breadth computation
    edge_q = (
        select(CapabilityEdge.source_id, CapabilityEdge.target_id)
        .where(
            CapabilityEdge.edge_type.in_(_BREADTH_EDGE_TYPES),
            or_(
                CapabilityEdge.source_id.in_(cap_ids),
                CapabilityEdge.target_id.in_(cap_ids),
            ),
        )
    )
    edge_result = await db.execute(edge_q)
    # Build adjacency: cap_id → set of related cap_ids
    adjacency: dict[str, set[str]] = {}
    for src, tgt in edge_result.all():
        adjacency.setdefault(src, set()).add(tgt)
        adjacency.setdefault(tgt, set()).add(src)

    # Set of all capability_ids the user has evidence for
    user_cap_ids = set(by_cap.keys())

    scores: list[CapabilityScore] = []
    for cap_id, ev_list in by_cap.items():
        cap = capabilities.get(cap_id)
        if not cap or cap.status not in ("active", "deprecated"):
            continue

        # Depth (backward compatible with v1)
        depth, confidence, substantial = compute_score_from_evidence(
            ev_list, cap.decay_config, now
        )

        # Breadth: fraction of related capabilities that also have evidence
        related = adjacency.get(cap_id, set())
        if related:
            breadth_count = len(related & user_cap_ids)
            breadth = breadth_count / max(len(related), 1)
        else:
            breadth = 0.0

        # Recency
        recency = compute_recency(ev_list, now)

        # Velocity
        velocity = compute_velocity(ev_list, now)

        # Composite score
        composite = (
            DIMENSION_WEIGHTS["depth"] * depth
            + DIMENSION_WEIGHTS["breadth"] * breadth
            + DIMENSION_WEIGHTS["recency"] * recency
            + DIMENSION_WEIGHTS["velocity"] * velocity
        )
        composite = round(composite, 4)

        level, level_label = determine_level(
            composite, substantial, cap.level_definitions
        )

        # Verification mix
        mix: dict[str, int] = {}
        for ev in ev_list:
            if ev["status"] == "active":
                vl = ev.get("verification_level", "")
                mix[vl] = mix.get(vl, 0) + 1

        # Last verified
        active_dates = [
            ev.get("occurred_at", "")
            for ev in ev_list
            if ev["status"] == "active" and ev.get("occurred_at", "")
        ]
        last_verified = max(active_dates) if active_dates else None

        scores.append(
            CapabilityScore(
                capability_id=cap_id,
                capability_name=cap.canonical_name,
                level=level,
                level_label=level_label,
                score=composite,
                depth=round(depth, 4),
                breadth=round(breadth, 4),
                recency=round(recency, 4),
                velocity=round(velocity, 4),
                confidence=confidence,
                evidence_count=len([e for e in ev_list if e["status"] == "active"]),
                substantial_evidence_count=substantial,
                last_verified_at=last_verified,
                verification_mix=mix,
                scoring_version=SCORING_VERSION,
                computed_at=now,
            )
        )

    # Sort by composite score descending
    scores.sort(key=lambda s: s.score, reverse=True)

    # Persist to cache (full profile only)
    if cache_key and scores:
        import dataclasses

        await set_cached(
            cache_key,
            [dataclasses.asdict(s) for s in scores],
            ttl=300,
        )

    return scores
