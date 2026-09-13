"""Employer verification service — structured capability verification (ADR-015 D9).

When an employer completes a placement evaluation, this service:
  1. Validates capability ratings are scoped to the opportunity's requirements
  2. Creates an EmployerVerification record
  3. Auto-generates CapabilityEvidence rows (employer_verified — highest trust)
  4. Auto-generates an OutcomeEvent for the placement
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import Placement
from app.talent.models.employer import Opportunity
from app.talent.models.internship import EmployerVerification, OutcomeEvent
from app.talent.services.evidence import EvidenceService


class EmployerVerificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_verification(
        self,
        *,
        placement_id: str,
        employer_org_id: str,
        verified_by: str,
        user_id: str,
        capability_ratings: list[dict],
        overall_rating: float | None = None,
        overall_comment: str | None = None,
    ) -> EmployerVerification:
        """Create an employer verification for a completed placement.

        Validates:
          - Placement exists and belongs to the employer org
          - capability_ratings only reference capabilities from the
            opportunity's required ∪ preferred (scope enforcement)

        Side effects:
          - Creates CapabilityEvidence rows (employer_verified, weight 1.0)
          - Creates an OutcomeEvent (internship_completed or contract_project_completed)
        """
        # --- Validate placement ---
        placement = await self.db.get(Placement, placement_id)
        if not placement:
            raise ValueError("Placement not found")
        if placement.employer_org_id != employer_org_id:
            raise ValueError("Placement does not belong to this employer")
        if placement.user_id != user_id:
            raise ValueError("User does not match the placement")

        # --- Load opportunity for scope enforcement ---
        opportunity = await self.db.get(Opportunity, placement.opportunity_id)
        if not opportunity:
            raise ValueError("Opportunity not found for this placement")

        # Build the set of capability_ids the employer is allowed to rate
        allowed_cap_ids: set[str] = set()
        for cap_entry in (opportunity.required_capabilities or []):
            cid = cap_entry.get("capability_id", "")
            if cid:
                allowed_cap_ids.add(cid)
        for cap_entry in (opportunity.preferred_capabilities or []):
            cid = cap_entry.get("capability_id", "")
            if cid:
                allowed_cap_ids.add(cid)

        # --- Validate capability_ratings scope ---
        for rating in capability_ratings:
            cap_id = rating.get("capability_id", "")
            if not cap_id:
                raise ValueError("Each capability_rating must have a capability_id")
            if cap_id not in allowed_cap_ids:
                raise ValueError(
                    f"Capability {cap_id} is not in the opportunity's "
                    "required or preferred capabilities — "
                    "employers can only rate capabilities observed in the placement"
                )
            score = rating.get("score")
            if score is not None and not (0 <= score <= 5):
                raise ValueError(
                    f"Capability rating score must be in [0, 5], got {score}"
                )

        # --- Validate overall_rating (0-5 scale, matching schema) ---
        if overall_rating is not None and not (0 <= overall_rating <= 5):
            raise ValueError("overall_rating must be in [0, 5]")

        # --- Create the verification record ---
        now = datetime.now(UTC)
        verification = EmployerVerification(
            placement_id=placement_id,
            employer_org_id=employer_org_id,
            verified_by=verified_by,
            user_id=user_id,
            capability_ratings=capability_ratings,
            overall_rating=overall_rating,
            overall_comment=overall_comment,
        )
        self.db.add(verification)
        await self.db.flush()

        # --- Auto-generate capability evidence rows ---
        evidence_svc = EvidenceService(self.db)
        for rating in capability_ratings:
            cap_id = rating["capability_id"]
            score = rating.get("score")
            await evidence_svc.record_evidence(
                user_id=user_id,
                capability_id=cap_id,
                source_type="employment_verification",
                source_id=verification.id,
                verification_level="employer_verified",
                occurred_at=now,
                org_id=employer_org_id,
                # Normalize 0-5 rating to [0,1] for evidence scoring
                score_normalized=score / 5.0 if score is not None else None,
                confidence=1.0,
                metadata={
                    "placement_id": placement_id,
                    "opportunity_id": placement.opportunity_id,
                    "verified_by": verified_by,
                    "level_observed": rating.get("level_observed"),
                    "comment": rating.get("comment"),
                },
            )

        # --- Auto-generate outcome event ---
        # Determine event type from opportunity type
        opp_type = opportunity.opportunity_type
        if opp_type in ("internship", "apprenticeship", "campus_project"):
            event_type = "internship_completed"
        elif opp_type in ("contract", "freelance", "project_role"):
            event_type = "contract_project_completed"
        else:
            event_type = "internship_completed"  # safe default

        outcome = OutcomeEvent(
            user_id=user_id,
            event_type=event_type,
            source_type="employer_verification",
            source_id=verification.id,
            occurred_at=now,
            extra={
                "placement_id": placement_id,
                "opportunity_id": placement.opportunity_id,
                "employer_org_id": employer_org_id,
                "opportunity_type": opp_type,
                "overall_rating": float(overall_rating) if overall_rating else None,
            },
        )
        self.db.add(outcome)
        await self.db.flush()

        return verification
