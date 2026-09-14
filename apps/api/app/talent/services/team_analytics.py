"""Team skill analytics — org-level capability inventory and gap analysis (N9).

Aggregates capability profiles across org members to show:
- Team skill distribution (which capabilities the team has)
- Team gaps (capabilities needed but no one has)
- Skill coverage matrix (who covers what)
- Team strength areas and weaknesses
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import OrgMember
from app.talent.models.employer import Opportunity
from app.talent.services.scoring import compute_capability_profile


@dataclass(frozen=True, slots=True)
class TeamSkillSummary:
    """Per-capability aggregate across all org members."""

    capability_id: str
    capability_name: str
    team_members_with_skill: int
    avg_level: float
    max_level: int
    min_level: int
    total_evidence: int


@dataclass(slots=True)
class TeamAnalytics:
    """Complete team skill analytics for an org."""

    org_id: str
    total_members: int
    total_capabilities_covered: int
    skill_distribution: list[TeamSkillSummary]
    team_strengths: list[str]  # top 5 capabilities by avg level
    team_gaps: list[str]  # capabilities with 0 coverage


class TeamAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_team_analytics(self, org_id: str) -> TeamAnalytics:
        """Compute skill analytics for all members of an org."""
        member_ids = await self._get_org_member_ids(org_id)
        if not member_ids:
            return TeamAnalytics(
                org_id=org_id,
                total_members=0,
                total_capabilities_covered=0,
                skill_distribution=[],
                team_strengths=[],
                team_gaps=[],
            )

        # Collect capability profiles for all members
        cap_data: dict[str, dict] = defaultdict(
            lambda: {
                "name": "",
                "levels": [],
                "evidence_count": 0,
                "member_ids": set(),
            }
        )

        for user_id in member_ids:
            profile = await compute_capability_profile(self.db, user_id)
            for score in profile:
                entry = cap_data[score.capability_id]
                entry["name"] = score.capability_name
                entry["levels"].append(score.level)
                entry["evidence_count"] += score.evidence_count
                entry["member_ids"].add(user_id)

        distribution: list[TeamSkillSummary] = []
        for cap_id, data in cap_data.items():
            levels = data["levels"]
            distribution.append(
                TeamSkillSummary(
                    capability_id=cap_id,
                    capability_name=data["name"],
                    team_members_with_skill=len(data["member_ids"]),
                    avg_level=round(sum(levels) / len(levels), 2) if levels else 0.0,
                    max_level=max(levels) if levels else 0,
                    min_level=min(levels) if levels else 0,
                    total_evidence=data["evidence_count"],
                )
            )

        # Sort by avg_level descending
        distribution.sort(key=lambda s: s.avg_level, reverse=True)

        # Top 5 strengths
        strengths = [s.capability_name for s in distribution[:5]]

        # Gaps: capabilities in open opportunities for this org but not in team
        team_cap_ids = set(cap_data.keys())
        gaps = await self._find_org_gaps(org_id, team_cap_ids)

        return TeamAnalytics(
            org_id=org_id,
            total_members=len(member_ids),
            total_capabilities_covered=len(cap_data),
            skill_distribution=distribution,
            team_strengths=strengths,
            team_gaps=gaps,
        )

    async def get_skill_coverage_matrix(
        self,
        org_id: str,
        capability_ids: list[str] | None = None,
    ) -> list[dict]:
        """Who in the org covers which capabilities.

        Returns: [{capability_id, capability_name, members: [{user_id, level, evidence_count}]}]
        """
        member_ids = await self._get_org_member_ids(org_id)
        if not member_ids:
            return []

        matrix: dict[str, dict] = defaultdict(
            lambda: {"capability_name": "", "members": []}
        )

        for user_id in member_ids:
            profile = await compute_capability_profile(
                self.db, user_id, capability_ids=capability_ids
            )
            for score in profile:
                entry = matrix[score.capability_id]
                entry["capability_name"] = score.capability_name
                entry["members"].append(
                    {
                        "user_id": user_id,
                        "level": score.level,
                        "evidence_count": score.evidence_count,
                    }
                )

        return [
            {
                "capability_id": cap_id,
                "capability_name": data["capability_name"],
                "members": data["members"],
            }
            for cap_id, data in matrix.items()
        ]

    async def compare_team_to_requirements(
        self,
        org_id: str,
        opportunity_id: str,
    ) -> dict:
        """Compare team's capabilities against an opportunity's requirements."""
        opp = await self.db.get(Opportunity, opportunity_id)
        if not opp:
            return {
                "fully_covered": [],
                "partially_covered": [],
                "not_covered": [],
                "coverage_score": 0.0,
            }

        required_caps = opp.required_capabilities or []
        if not required_caps:
            return {
                "fully_covered": [],
                "partially_covered": [],
                "not_covered": [],
                "coverage_score": 1.0,
            }

        # Build team's max level per capability
        member_ids = await self._get_org_member_ids(org_id)
        team_levels: dict[str, int] = defaultdict(int)
        team_names: dict[str, str] = {}

        cap_ids = [r.get("capability_id", "") for r in required_caps if r.get("capability_id")]
        for user_id in member_ids:
            profile = await compute_capability_profile(
                self.db, user_id, capability_ids=cap_ids
            )
            for score in profile:
                team_levels[score.capability_id] = max(
                    team_levels[score.capability_id], score.level
                )
                team_names[score.capability_id] = score.capability_name

        fully_covered = []
        partially_covered = []
        not_covered = []

        for req in required_caps:
            cap_id = req.get("capability_id", "")
            cap_name = req.get("capability_name", cap_id)
            min_level = req.get("min_level", 1)

            team_level = team_levels.get(cap_id, 0)
            actual_name = team_names.get(cap_id, cap_name)

            entry = {
                "capability_id": cap_id,
                "capability_name": actual_name,
                "required_level": min_level,
                "team_max_level": team_level,
            }

            if team_level >= min_level:
                fully_covered.append(entry)
            elif team_level > 0:
                partially_covered.append(entry)
            else:
                not_covered.append(entry)

        total = len(required_caps)
        score = len(fully_covered) / total if total > 0 else 0.0

        return {
            "fully_covered": fully_covered,
            "partially_covered": partially_covered,
            "not_covered": not_covered,
            "coverage_score": round(score, 3),
        }

    async def _get_org_member_ids(self, org_id: str) -> list[str]:
        """Get all member user IDs for an org."""
        q = select(OrgMember.user_id).where(OrgMember.org_id == org_id)
        result = await self.db.execute(q)
        return [row[0] for row in result.all()]

    async def _find_org_gaps(
        self, org_id: str, team_cap_ids: set[str]
    ) -> list[str]:
        """Find capabilities required by org's open opportunities but not in team."""
        q = select(Opportunity.required_capabilities).where(
            Opportunity.employer_org_id == org_id,
            Opportunity.status == "open",
        )
        result = await self.db.execute(q)
        needed: set[str] = set()
        for (req_caps,) in result.all():
            if req_caps:
                for req in req_caps:
                    cap_name = req.get("capability_name", req.get("capability_id", ""))
                    cap_id = req.get("capability_id", "")
                    if cap_id and cap_id not in team_cap_ids:
                        needed.add(cap_name)
        return sorted(needed)
