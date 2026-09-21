"""Personalized learning plan based on skill gaps (ADR-015 upgrade C6).

Given a user's current capability profile and career path gaps,
finds platform content (Skill Packs, Assessments, Project Templates)
mapped to missing capabilities via CapabilityMapping.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.capability import CapabilityMapping
from app.talent.models.employer import Opportunity
from app.talent.services.scoring import compute_capability_profile


@dataclass(frozen=True, slots=True)
class ContentRecommendation:
    """A piece of platform content that teaches a missing capability."""

    source_type: str  # skill, skill_pack, project_template, assessment_blueprint, etc.
    source_id: str
    coverage_weight: float  # how much this content covers the capability


@dataclass(frozen=True, slots=True)
class LearningRecommendation:
    """A gap + recommended content to close it."""

    capability_id: str
    capability_name: str
    current_level: int
    target_level: int
    gap_size: int
    recommended_content: list[ContentRecommendation]


class LearningPlanService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_plan(
        self,
        user_id: str,
        *,
        target_opportunity_id: str | None = None,
        target_capabilities: list[dict] | None = None,
        max_recommendations_per_gap: int = 5,
    ) -> list[LearningRecommendation]:
        """Generate a personalized learning plan.

        Args:
            user_id: Target learner
            target_opportunity_id: If set, derive gaps from opportunity requirements
            target_capabilities: Explicit gap targets [{capability_id, min_level}]
            max_recommendations_per_gap: Max content items per gap

        Returns:
            Ordered list of learning recommendations, most impactful first.
        """
        # 1. Get user's current capability scores
        profile = await compute_capability_profile(self.db, user_id)
        user_levels: dict[str, tuple[int, str]] = {
            s.capability_id: (s.level, s.capability_name) for s in profile
        }

        # 2. Determine target capabilities
        gaps: list[dict] = []

        if target_opportunity_id:
            opp = await self.db.get(Opportunity, target_opportunity_id)
            if opp:
                for req in opp.required_capabilities or []:
                    cap_id = req.get("capability_id", "")
                    min_level = req.get("min_level", 1)
                    cap_name = req.get("capability_name", cap_id)
                    current = user_levels.get(cap_id, (0, cap_name))
                    if current[0] < min_level:
                        gaps.append(
                            {
                                "capability_id": cap_id,
                                "capability_name": current[1] or cap_name,
                                "current_level": current[0],
                                "target_level": min_level,
                            }
                        )
                for pref in opp.preferred_capabilities or []:
                    cap_id = pref.get("capability_id", "")
                    min_level = pref.get("min_level", 1)
                    cap_name = pref.get("capability_name", cap_id)
                    current = user_levels.get(cap_id, (0, cap_name))
                    if current[0] < min_level:
                        gaps.append(
                            {
                                "capability_id": cap_id,
                                "capability_name": current[1] or cap_name,
                                "current_level": current[0],
                                "target_level": min_level,
                            }
                        )

        elif target_capabilities:
            for tc in target_capabilities:
                cap_id = tc.get("capability_id", "")
                min_level = tc.get("min_level", 1)
                cap_name = tc.get("capability_name", cap_id)
                current = user_levels.get(cap_id, (0, cap_name))
                if current[0] < min_level:
                    gaps.append(
                        {
                            "capability_id": cap_id,
                            "capability_name": current[1] or cap_name,
                            "current_level": current[0],
                            "target_level": min_level,
                        }
                    )

        if not gaps:
            return []

        # 3. For each gap, find mapped content
        gap_cap_ids = [g["capability_id"] for g in gaps]
        mapping_q = (
            select(CapabilityMapping)
            .where(CapabilityMapping.capability_id.in_(gap_cap_ids))
            .order_by(CapabilityMapping.contribution_weight.desc())
        )
        result = await self.db.execute(mapping_q)
        mappings = result.scalars().all()

        # Group mappings by capability_id
        by_cap: dict[str, list[CapabilityMapping]] = {}
        for m in mappings:
            by_cap.setdefault(m.capability_id, []).append(m)

        # 4. Build recommendations
        recommendations: list[LearningRecommendation] = []
        for gap in gaps:
            cap_id = gap["capability_id"]
            content_mappings = by_cap.get(cap_id, [])
            content = [
                ContentRecommendation(
                    source_type=m.source_type,
                    source_id=m.source_id,
                    coverage_weight=float(m.contribution_weight),
                )
                for m in content_mappings[:max_recommendations_per_gap]
            ]

            gap_size = gap["target_level"] - gap["current_level"]
            recommendations.append(
                LearningRecommendation(
                    capability_id=cap_id,
                    capability_name=gap["capability_name"],
                    current_level=gap["current_level"],
                    target_level=gap["target_level"],
                    gap_size=gap_size,
                    recommended_content=content,
                )
            )

        # Sort by gap size descending (biggest gaps first)
        recommendations.sort(key=lambda r: r.gap_size, reverse=True)
        return recommendations
