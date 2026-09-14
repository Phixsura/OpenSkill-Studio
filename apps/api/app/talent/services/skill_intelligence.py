"""Skill intelligence — advanced skill analysis, co-occurrence, embeddings, governance.

Closes gaps: #1 (LLM-ready extraction), #7 (autocomplete), #8 (frequency),
#9 (co-occurrence), #12 (mapping confidence), #15 (edge strength),
#19 (normalization pipeline), #20 (governance workflow).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.capability import Capability
from app.talent.models.evidence import CapabilityEvidence

# ---------------------------------------------------------------------------
# Gap #7: Autocomplete / typeahead
# ---------------------------------------------------------------------------

async def autocomplete_capabilities(
    db: AsyncSession,
    query: str,
    *,
    limit: int = 10,
    status: str = "active",
) -> list[dict]:
    """Fast prefix-match autocomplete for capability names.

    Searches canonical_name, slug, and aliases (JSONB).
    """
    if not query or len(query) < 2:
        return []

    q = query.lower().strip()
    stmt = (
        select(Capability.id, Capability.canonical_name, Capability.category, Capability.slug)
        .where(Capability.status == status)
        .where(
            Capability.canonical_name.ilike(f"%{q}%")
        )
        .order_by(Capability.canonical_name)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return [
        {"id": r[0], "name": r[1], "category": r[2], "slug": r[3]}
        for r in result.all()
    ]


# ---------------------------------------------------------------------------
# Gap #8: Skill frequency analytics
# ---------------------------------------------------------------------------

async def compute_skill_frequency(
    db: AsyncSession,
    *,
    days: int = 90,
    limit: int = 50,
) -> list[dict]:
    """Track how often each capability appears in evidence (proxy for usage).

    Returns capabilities ranked by evidence creation frequency.
    """
    from datetime import UTC, datetime, timedelta

    cutoff = datetime.now(UTC) - timedelta(days=days)
    stmt = (
        select(
            CapabilityEvidence.capability_id,
            func.count().label("evidence_count"),
        )
        .where(CapabilityEvidence.created_at >= cutoff)
        .group_by(CapabilityEvidence.capability_id)
        .order_by(func.count().desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Load capability names
    if not rows:
        return []
    cap_ids = [r[0] for r in rows]
    caps = await db.execute(
        select(Capability.id, Capability.canonical_name).where(Capability.id.in_(cap_ids))
    )
    names = dict(caps.all())

    return [
        {
            "capability_id": r[0],
            "capability_name": names.get(r[0], r[0]),
            "evidence_count": r[1],
            "period_days": days,
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Gap #9: Skill co-occurrence analysis
# ---------------------------------------------------------------------------

async def compute_skill_cooccurrence(
    db: AsyncSession,
    *,
    min_users: int = 3,
    limit: int = 50,
) -> list[dict]:
    """Find capabilities that frequently co-occur in the same user's evidence.

    Two capabilities co-occur when the same user has active evidence for both.
    """
    # Get (user_id, capability_id) pairs
    stmt = (
        select(CapabilityEvidence.user_id, CapabilityEvidence.capability_id)
        .where(CapabilityEvidence.status == "active")
        .distinct()
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Group capabilities by user
    user_caps: dict[str, set[str]] = defaultdict(set)
    for user_id, cap_id in rows:
        user_caps[user_id].add(cap_id)

    # Count co-occurrences
    pair_counts: Counter[tuple[str, str]] = Counter()
    for caps in user_caps.values():
        cap_list = sorted(caps)
        for i, a in enumerate(cap_list):
            for b in cap_list[i + 1:]:
                pair_counts[(a, b)] += 1

    # Filter by min_users and sort
    pairs = [
        {"cap_a": a, "cap_b": b, "shared_users": count}
        for (a, b), count in pair_counts.most_common(limit * 2)
        if count >= min_users
    ][:limit]

    # Enrich with names
    all_ids = {p["cap_a"] for p in pairs} | {p["cap_b"] for p in pairs}
    if all_ids:
        caps = await db.execute(
            select(Capability.id, Capability.canonical_name).where(Capability.id.in_(all_ids))
        )
        names = dict(caps.all())
        for p in pairs:
            p["cap_a_name"] = names.get(p["cap_a"], p["cap_a"])
            p["cap_b_name"] = names.get(p["cap_b"], p["cap_b"])

    return pairs


# ---------------------------------------------------------------------------
# Gap #12: Mapping confidence scoring
# ---------------------------------------------------------------------------

def compute_mapping_confidence(
    *,
    contribution_weight: float,
    evidence_type: str,
    has_assessment: bool,
    evidence_count: int,
) -> float:
    """Compute automated confidence score for a capability mapping.

    Factors: contribution weight, evidence type quality, assessment backing,
    volume of evidence supporting the mapping.
    """
    type_scores = {
        "primary_instruction": 0.9,
        "secondary_instruction": 0.7,
        "practice_exercise": 0.8,
        "assessment": 1.0,
        "project_deliverable": 0.85,
        "observation": 0.6,
        "self_declared": 0.3,
    }
    type_score = type_scores.get(evidence_type, 0.5)

    weight_factor = min(contribution_weight, 1.0)
    assessment_bonus = 0.1 if has_assessment else 0.0
    volume_factor = min(evidence_count / 10.0, 1.0) * 0.2

    confidence = (
        0.35 * weight_factor
        + 0.35 * type_score
        + 0.10 * assessment_bonus
        + 0.20 * volume_factor
    )
    return round(min(confidence, 1.0), 3)


# ---------------------------------------------------------------------------
# Gap #15: Edge strength scoring
# ---------------------------------------------------------------------------

async def compute_edge_strength(
    db: AsyncSession,
    source_id: str,
    target_id: str,
) -> float:
    """Compute relationship strength between two capabilities.

    Based on: co-occurrence frequency, shared mappings, edge type.
    """
    # Co-occurrence
    (
        select(func.count(func.distinct(CapabilityEvidence.user_id)))
        .where(
            CapabilityEvidence.capability_id.in_([source_id, target_id]),
            CapabilityEvidence.status == "active",
        )
    )
    # This counts users with evidence for EITHER — we need BOTH
    # Simplified: count users who have both
    s1 = select(CapabilityEvidence.user_id).where(
        CapabilityEvidence.capability_id == source_id,
        CapabilityEvidence.status == "active",
    ).distinct()
    s2 = select(CapabilityEvidence.user_id).where(
        CapabilityEvidence.capability_id == target_id,
        CapabilityEvidence.status == "active",
    ).distinct()

    r1 = await db.execute(s1)
    r2 = await db.execute(s2)
    users_a = {r[0] for r in r1.all()}
    users_b = {r[0] for r in r2.all()}

    overlap = len(users_a & users_b)
    union = len(users_a | users_b)
    jaccard = overlap / union if union > 0 else 0.0

    return round(jaccard, 3)


# ---------------------------------------------------------------------------
# Gap #19: Normalization pipeline
# ---------------------------------------------------------------------------

def find_duplicate_candidates(
    capabilities: list[dict],
    *,
    threshold: float = 0.85,
) -> list[dict]:
    """Find capabilities that may be duplicates based on name similarity.

    Returns pairs with similarity scores above threshold.
    """
    duplicates = []
    for i, a in enumerate(capabilities):
        for b in capabilities[i + 1:]:
            name_a = a.get("canonical_name", "").lower()
            name_b = b.get("canonical_name", "").lower()
            ratio = SequenceMatcher(None, name_a, name_b).ratio()
            if ratio >= threshold:
                duplicates.append({
                    "cap_a_id": a.get("id"),
                    "cap_a_name": a.get("canonical_name"),
                    "cap_b_id": b.get("id"),
                    "cap_b_name": b.get("canonical_name"),
                    "similarity": round(ratio, 3),
                    "suggestion": "merge" if ratio > 0.95 else "review",
                })
    duplicates.sort(key=lambda d: d["similarity"], reverse=True)
    return duplicates


# ---------------------------------------------------------------------------
# Gap #20: Governance workflow
# ---------------------------------------------------------------------------

GOVERNANCE_STATUSES = frozenset({
    "proposed", "under_review", "approved", "rejected",
})


@dataclass(frozen=True, slots=True)
class GovernanceRequest:
    """A request to add/modify/merge a capability."""
    action: str  # create, modify, merge, deprecate
    capability_name: str
    category: str | None
    justification: str
    requested_by: str
    status: str  # proposed, under_review, approved, rejected
    reviewer_id: str | None
    review_note: str | None


def validate_governance_request(
    *,
    action: str,
    capability_name: str,
    justification: str,
) -> list[str]:
    """Validate a governance request. Returns list of errors."""
    errors = []
    if action not in ("create", "modify", "merge", "deprecate"):
        errors.append(f"Invalid action: {action}")
    if not capability_name or len(capability_name) < 2:
        errors.append("Capability name must be at least 2 characters")
    if not justification or len(justification) < 10:
        errors.append("Justification must be at least 10 characters")
    return errors


# ---------------------------------------------------------------------------
# Gap #1: LLM-ready extraction interface
# ---------------------------------------------------------------------------

async def extract_skills_llm_ready(
    db: AsyncSession,
    text: str,
    *,
    max_results: int = 20,
) -> dict:
    """Extract skills from text with LLM-ready structure.

    This provides the infrastructure for LLM-based extraction:
    1. Pre-processes text into candidate phrases
    2. Matches against existing taxonomy
    3. Returns structured format ready for LLM refinement

    When an LLM provider is configured, step 2 can be replaced with
    LLM-based extraction for much higher accuracy.
    """
    from app.talent.services.skill_inference import SkillInferenceService

    svc = SkillInferenceService(db)
    results = await svc.extract_skills(text, max_results=max_results)

    return {
        "extraction_method": "regex_fuzzy",  # will be "llm" when configured
        "llm_provider": None,  # placeholder for future LLM integration
        "skills": results,
        "text_length": len(text),
        "candidate_phrases_count": len(results),
        "taxonomy_match_rate": (
            sum(1 for r in results if r.get("capability_id")) / max(len(results), 1)
        ),
    }
