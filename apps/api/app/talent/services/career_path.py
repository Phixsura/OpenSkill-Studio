"""Career path prediction — gap-aware opportunity discovery (ADR-015 D4E).

Given a user's current capability profile, finds opportunities that are
1-2 capability-gaps away and suggests specific learning actions to close
each gap. Surfaces "Improve my match" action items.

Algorithm:
  1. Compute user's current capability scores
  2. For each open opportunity within reach (≤2 unmet required caps):
     a. Identify the missing capabilities + level gaps
     b. Score reachability: fewer/smaller gaps = more reachable
     c. Suggest concrete actions per gap (e.g. "add 2 more evidence items")
  3. Rank by reachability × opportunity attractiveness
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.employer import Opportunity
from app.talent.services.scoring import compute_capability_profile


@dataclass(frozen=True, slots=True)
class SkillGap:
    """A single capability gap between user's level and requirement."""

    capability_id: str
    capability_name: str
    current_level: int
    required_level: int
    gap_size: int  # required - current
    action: str  # suggested action text


@dataclass(frozen=True, slots=True)
class CareerPathSuggestion:
    """An opportunity the user could reach with specific skill improvements."""

    opportunity_id: str
    opportunity_title: str
    opportunity_type: str
    employer_org_id: str
    reachability_score: float  # 0-1, higher = easier to reach
    gaps: list[SkillGap]
    total_gap_size: int
    estimated_actions: int  # total number of discrete actions needed


# Maximum unmet required capabilities for an opportunity to be "reachable"
MAX_REACHABLE_GAPS = 3
# Maximum level gap per capability
MAX_LEVEL_GAP = 3


def _suggest_action(current_level: int, required_level: int, gap: int) -> str:
    """Generate a human-readable suggestion for closing a specific gap."""
    if current_level == 0:
        if required_level <= 2:
            return "Complete a foundational course or add 3+ evidence items"
        return "Start with introductory practice and build evidence portfolio"
    if gap == 1:
        return "Add 2-3 more verified evidence items to advance one level"
    if gap == 2:
        return "Complete an assessment or accumulate 5+ new evidence items"
    return f"Significant upskilling needed — target {gap} level advancement"


async def predict_career_paths(
    db: AsyncSession,
    user_id: str,
    *,
    max_results: int = 10,
    include_types: list[str] | None = None,
) -> list[CareerPathSuggestion]:
    """Find reachable opportunities and suggest gap-closing actions.

    Args:
        db: Database session
        user_id: Target user
        max_results: Maximum suggestions to return
        include_types: Filter by opportunity type (internship, job, project, etc.)

    Returns:
        Ranked list of career path suggestions
    """
    # 1. Get user's current capability profile
    profile = await compute_capability_profile(db, user_id)
    user_levels: dict[str, tuple[int, str]] = {
        s.capability_id: (s.level, s.capability_name) for s in profile
    }

    # 2. Load open opportunities
    q = select(Opportunity).where(Opportunity.status == "open")
    if include_types:
        q = q.where(Opportunity.opportunity_type.in_(include_types))
    q = q.limit(200)  # bounded for performance

    result = await db.execute(q)
    opportunities = result.scalars().all()

    suggestions: list[CareerPathSuggestion] = []

    for opp in opportunities:
        required_caps = opp.required_capabilities or []
        if not required_caps:
            continue

        gaps: list[SkillGap] = []

        for req in required_caps:
            cap_id = req.get("capability_id", "")
            cap_name = req.get("capability_name", cap_id)
            min_level = req.get("min_level", 1)

            current_level = 0
            if cap_id in user_levels:
                current_level = user_levels[cap_id][0]
                cap_name = user_levels[cap_id][1] or cap_name

            gap_size = max(0, min_level - current_level)
            if gap_size > 0 and gap_size <= MAX_LEVEL_GAP:
                gaps.append(
                    SkillGap(
                        capability_id=cap_id,
                        capability_name=cap_name,
                        current_level=current_level,
                        required_level=min_level,
                        gap_size=gap_size,
                        action=_suggest_action(current_level, min_level, gap_size),
                    )
                )

        # Skip if too many gaps or no gaps (already fully qualified)
        if len(gaps) == 0 or len(gaps) > MAX_REACHABLE_GAPS:
            continue

        # Also skip if any single gap is too large
        if any(g.gap_size > MAX_LEVEL_GAP for g in gaps):
            continue

        total_gap = sum(g.gap_size for g in gaps)

        # Reachability: inverse of total gap, normalized
        # 1 gap of size 1 → 0.9, 3 gaps of size 3 → 0.1
        max_possible_gap = MAX_REACHABLE_GAPS * MAX_LEVEL_GAP
        reachability = max(0.0, 1.0 - (total_gap / max_possible_gap))

        # Bonus for having some capabilities already met
        met_count = len(required_caps) - len(gaps)
        if len(required_caps) > 0:
            coverage_bonus = met_count / max(len(required_caps), 1) * 0.2
            reachability = min(1.0, reachability + coverage_bonus)

        suggestions.append(
            CareerPathSuggestion(
                opportunity_id=opp.id,
                opportunity_title=opp.title,
                opportunity_type=opp.opportunity_type,
                employer_org_id=opp.employer_org_id,
                reachability_score=round(reachability, 3),
                gaps=gaps,
                total_gap_size=total_gap,
                estimated_actions=len(gaps),
            )
        )

    # Sort by reachability (highest first)
    suggestions.sort(key=lambda s: s.reachability_score, reverse=True)
    return suggestions[:max_results]
