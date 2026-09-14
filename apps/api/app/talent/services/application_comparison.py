"""Application comparison — side-by-side candidate comparison for employers (N16).

Given multiple application IDs for the same opportunity, produces a
structured comparison matrix across capability scores, evidence,
credentials, and interview feedback.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import Application
from app.talent.models.assessment import Credential
from app.talent.models.employer import Opportunity
from app.talent.models.endorsement import SkillEndorsement
from app.talent.models.evidence import CapabilityEvidence
from app.talent.models.scorecard import InterviewScorecard
from app.talent.services.scoring import compute_capability_profile

# Maximum applications in a single comparison
MAX_COMPARE = 10


@dataclass(slots=True)
class CandidateComparison:
    """Comparison data for a single candidate."""

    application_id: str
    user_id: str
    status: str
    capability_scores: dict[str, float]
    credential_count: int
    evidence_count: int
    endorsement_count: int
    match_score: float | None
    interview_ratings: dict[str, float | None]
    overall_rank: int


class ApplicationComparisonService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def compare(
        self,
        opportunity_id: str,
        application_ids: list[str],
    ) -> list[CandidateComparison]:
        """Compare candidates side-by-side for the same opportunity."""
        if len(application_ids) < 2:
            raise ValueError("At least 2 applications required for comparison")
        if len(application_ids) > MAX_COMPARE:
            raise ValueError(f"Maximum {MAX_COMPARE} applications per comparison")

        # Load and validate applications
        apps: list[Application] = []
        for app_id in application_ids:
            app = await self.db.get(Application, app_id)
            if not app:
                raise ValueError(f"Application {app_id} not found")
            if app.opportunity_id != opportunity_id:
                raise ValueError(
                    f"Application {app_id} does not belong to opportunity {opportunity_id}"
                )
            apps.append(app)

        # Load opportunity for required capabilities
        opp = await self.db.get(Opportunity, opportunity_id)
        required_cap_ids = []
        if opp and opp.required_capabilities:
            required_cap_ids = [
                r.get("capability_id", "")
                for r in opp.required_capabilities
                if r.get("capability_id")
            ]

        comparisons: list[CandidateComparison] = []

        for app in apps:
            # Capability scores
            cap_scores: dict[str, float] = {}
            if required_cap_ids:
                profile = await compute_capability_profile(
                    self.db, app.user_id, capability_ids=required_cap_ids
                )
                cap_scores = {s.capability_id: s.score for s in profile}

            # Credential count
            cred_q = select(func.count()).where(
                Credential.user_id == app.user_id,
                Credential.status == "active",
            )
            cred_count = (await self.db.execute(cred_q)).scalar() or 0

            # Evidence count
            ev_q = select(func.count()).where(
                CapabilityEvidence.user_id == app.user_id,
                CapabilityEvidence.status == "active",
            )
            ev_count = (await self.db.execute(ev_q)).scalar() or 0

            # Endorsement count
            end_q = select(func.count()).where(
                SkillEndorsement.user_id == app.user_id,
                SkillEndorsement.status == "accepted",
            )
            end_count = (await self.db.execute(end_q)).scalar() or 0

            # Interview scorecard ratings
            from app.talent.models.application import InterviewStage

            stage_q = select(InterviewStage.id).where(
                InterviewStage.application_id == app.id
            )
            stage_result = await self.db.execute(stage_q)
            stage_ids = [r[0] for r in stage_result.all()]

            interview_ratings: dict[str, float | None] = {}
            if stage_ids:
                for stage_id in stage_ids:
                    stage = await self.db.get(InterviewStage, stage_id)
                    if not stage:
                        continue
                    rating_q = select(func.avg(InterviewScorecard.overall_rating)).where(
                        InterviewScorecard.interview_stage_id == stage_id,
                        InterviewScorecard.submitted_at.isnot(None),
                    )
                    avg_rating = (await self.db.execute(rating_q)).scalar()
                    interview_ratings[stage.stage_type] = (
                        round(float(avg_rating), 2) if avg_rating else None
                    )

            # Match score from evidence bundle
            match_score = None
            if app.evidence_bundle and isinstance(app.evidence_bundle, dict):
                match_score = app.evidence_bundle.get("match_score")

            comparisons.append(
                CandidateComparison(
                    application_id=app.id,
                    user_id=app.user_id,
                    status=app.status,
                    capability_scores=cap_scores,
                    credential_count=cred_count,
                    evidence_count=ev_count,
                    endorsement_count=end_count,
                    match_score=match_score,
                    interview_ratings=interview_ratings,
                    overall_rank=0,  # computed below
                )
            )

        # Rank by composite quality: cap_scores avg + credential bonus + evidence bonus
        for comp in comparisons:
            avg_cap = (
                sum(comp.capability_scores.values()) / max(len(comp.capability_scores), 1)
                if comp.capability_scores
                else 0
            )
            comp_score = avg_cap * 0.5 + min(comp.credential_count / 5, 1) * 0.2 + min(comp.evidence_count / 20, 1) * 0.3
            comp.match_score = comp.match_score or round(comp_score, 3)

        # Sort by match_score descending and assign ranks
        comparisons.sort(key=lambda c: c.match_score or 0, reverse=True)
        for i, comp in enumerate(comparisons):
            comp.overall_rank = i + 1

        return comparisons
