"""Capability scoring engine — versioned, reproducible, decay-aware (ADR-015 D3).

Algorithm v1.0.0:
  1. Filter active, non-expired evidence.
  2. Per evidence: effective = base × verification_weight × confidence × freshness.
  3. Aggregate: Bayesian-shrunk mean (k=3, prior=0.5).
  4. Level = threshold lookup from capability definitions or platform default.
  5. Confidence = 1 - (k / (n + k)).
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.capability import Capability
from app.talent.models.evidence import (
    VERIFICATION_WEIGHTS,
    CapabilityEvidence,
)

SCORING_VERSION = "1.0.0"

# Bayesian shrinkage: k=3 balances single-data-point noise with prior
SHRINKAGE_K = 3
SHRINKAGE_PRIOR = 0.5

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


@dataclass(frozen=True, slots=True)
class CapabilityScore:
    """Derived capability score for a single (user, capability) pair."""

    capability_id: str
    capability_name: str
    level: int
    level_label: str
    score: float
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
    """Pure scoring computation.

    Returns (score, confidence, substantial_count).
    evidence_rows: list of dicts with keys:
        score_normalized, verification_level, confidence, occurred_at, status, expires_at
    """
    active = []
    for ev in evidence_rows:
        if ev["status"] != "active":
            continue
        if ev.get("expires_at") and ev["expires_at"] < now:
            continue
        active.append(ev)

    if not active:
        return 0.0, 0.0, 0

    effective_scores = []
    for ev in active:
        base = ev["score_normalized"] if ev["score_normalized"] is not None else 0.8
        ver_weight = VERIFICATION_WEIGHTS.get(ev["verification_level"], 0.5)
        conf = float(ev.get("confidence", 1.0))
        freshness = decay_factor(ev["occurred_at"], now, decay_config)
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
        if ev["verification_level"] in SUBSTANTIAL_VERIFICATION
    )

    return round(shrunk, 4), round(model_confidence, 4), substantial


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
) -> list[CapabilityScore]:
    """Compute derived capability scores for a user.

    If capability_ids is None, computes for all capabilities the user has
    evidence for.
    """
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

    scores: list[CapabilityScore] = []
    for cap_id, ev_list in by_cap.items():
        cap = capabilities.get(cap_id)
        if not cap or cap.status not in ("active", "deprecated"):
            continue

        score, confidence, substantial = compute_score_from_evidence(
            ev_list, cap.decay_config, now
        )
        level, level_label = determine_level(
            score, substantial, cap.level_definitions
        )

        # Verification mix
        mix: dict[str, int] = {}
        for ev in ev_list:
            if ev["status"] == "active":
                vl = ev["verification_level"]
                mix[vl] = mix.get(vl, 0) + 1

        # Last verified
        active_dates = [
            ev["occurred_at"]
            for ev in ev_list
            if ev["status"] == "active" and ev["occurred_at"]
        ]
        last_verified = max(active_dates) if active_dates else None

        scores.append(
            CapabilityScore(
                capability_id=cap_id,
                capability_name=cap.canonical_name,
                level=level,
                level_label=level_label,
                score=score,
                confidence=confidence,
                evidence_count=len([e for e in ev_list if e["status"] == "active"]),
                substantial_evidence_count=substantial,
                last_verified_at=last_verified,
                verification_mix=mix,
                scoring_version=SCORING_VERSION,
                computed_at=now,
            )
        )

    # Sort by score descending
    scores.sort(key=lambda s: s.score, reverse=True)
    return scores
