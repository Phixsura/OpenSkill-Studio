"""Evidence service — append-only evidence ledger operations (ADR-015 D2).

Evidence rows are immutable. The only mutation is status transitions:
active → superseded | voided. New/corrected evidence is always an INSERT
with supersedes_id pointing to the old row.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.evidence import (
    EVIDENCE_SOURCE_TYPES,
    VERIFICATION_LEVELS,
    CapabilityEvidence,
)


class EvidenceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_evidence(
        self,
        *,
        user_id: str,
        capability_id: str,
        source_type: str,
        source_id: str,
        verification_level: str,
        occurred_at: datetime,
        org_id: str | None = None,
        score_normalized: float | None = None,
        confidence: float = 1.0,
        expires_at: datetime | None = None,
        metadata: dict | None = None,
    ) -> CapabilityEvidence:
        """Record a new evidence row. Idempotent via partial unique index.

        If an active row already exists for (user, capability, source_type, source_id),
        it is superseded and a new row is inserted.
        """
        if source_type not in EVIDENCE_SOURCE_TYPES:
            raise ValueError(f"Invalid source_type: {source_type}")
        if verification_level not in VERIFICATION_LEVELS:
            raise ValueError(f"Invalid verification_level: {verification_level}")
        if score_normalized is not None and not (0 <= score_normalized <= 1):
            raise ValueError("score_normalized must be in [0, 1]")
        if not (0 <= confidence <= 1):
            raise ValueError("confidence must be in [0, 1]")

        # Check for existing active evidence
        existing = await self.db.execute(
            select(CapabilityEvidence).where(
                CapabilityEvidence.user_id == user_id,
                CapabilityEvidence.capability_id == capability_id,
                CapabilityEvidence.source_type == source_type,
                CapabilityEvidence.source_id == source_id,
                CapabilityEvidence.status == "active",
            )
        )
        old = existing.scalar_one_or_none()

        supersedes_id = None
        if old:
            # Supersede the existing row
            old.status = "superseded"
            supersedes_id = old.id

        evidence = CapabilityEvidence(
            user_id=user_id,
            capability_id=capability_id,
            source_type=source_type,
            source_id=source_id,
            org_id=org_id,
            score_normalized=score_normalized,
            confidence=confidence,
            verification_level=verification_level,
            occurred_at=occurred_at,
            expires_at=expires_at,
            supersedes_id=supersedes_id,
            extra=metadata or {},
        )
        self.db.add(evidence)
        await self.db.flush()
        return evidence

    async def void_evidence(
        self,
        evidence_id: str,
        *,
        reason: str | None = None,
    ) -> CapabilityEvidence | None:
        """Void an evidence row (retraction). Returns the voided row or None."""
        evidence = await self.db.get(CapabilityEvidence, evidence_id)
        if not evidence or evidence.status != "active":
            return None

        evidence.status = "voided"
        if reason:
            meta = dict(evidence.extra) if evidence.extra else {}
            meta["void_reason"] = reason
            evidence.extra = meta

        await self.db.flush()
        return evidence

    async def get_evidence_for_user(
        self,
        user_id: str,
        *,
        capability_id: str | None = None,
        status: str = "active",
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[CapabilityEvidence], int]:
        """List evidence for a user with pagination."""
        q = select(CapabilityEvidence).where(
            CapabilityEvidence.user_id == user_id,
            CapabilityEvidence.status == status,
        )
        if capability_id:
            q = q.where(CapabilityEvidence.capability_id == capability_id)

        from sqlalchemy import func

        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar() or 0

        q = q.order_by(CapabilityEvidence.occurred_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def get_provenance_chain(
        self,
        evidence_id: str,
        *,
        requesting_user_id: str | None = None,
    ) -> list[dict]:
        """Resolve the provenance chain for an evidence row.

        Each link checks access; inaccessible links are redacted.
        Full provenance resolution requires product model imports — deferred
        to a dedicated resolver that understands each source_type.
        """
        evidence = await self.db.get(CapabilityEvidence, evidence_id)
        if not evidence:
            return []

        chain = [
            {
                "type": evidence.source_type,
                "id": evidence.source_id,
                "evidence_id": evidence.id,
                "verification_level": evidence.verification_level,
                "occurred_at": evidence.occurred_at.isoformat() if evidence.occurred_at else None,
            }
        ]

        # Resolve deeper provenance per source_type.
        # Each resolver checks access; inaccessible links are redacted.
        deeper = await self._resolve_source_provenance(
            evidence.source_type,
            evidence.source_id,
            requesting_user_id=requesting_user_id,
        )
        chain.extend(deeper)

        return chain

    async def _resolve_source_provenance(
        self,
        source_type: str,
        source_id: str,
        *,
        requesting_user_id: str | None = None,
    ) -> list[dict]:
        """Walk the provenance tree from an evidence source to its roots.

        Resolves known source types to their parent records. Unknown types
        terminate the chain (no error). Inaccessible links are redacted.
        """
        from app.models.organization import OrgMember

        chain: list[dict] = []

        if source_type == "project_approval":
            # submission → project
            from app.models.project import Submission

            sub = await self.db.get(Submission, source_id)
            if not sub:
                return chain
            chain.append({
                "type": "submission",
                "id": sub.id,
                "label": f"Submission (status: {sub.status})",
            })
            if sub.project_id:
                from app.models.project import Project

                proj = await self.db.get(Project, sub.project_id)
                if proj:
                    # Check access — only show if requestor is in the org
                    if requesting_user_id:
                        member = await self.db.execute(
                            select(OrgMember.id).where(
                                OrgMember.org_id == proj.org_id,
                                OrgMember.user_id == requesting_user_id,
                            ).limit(1)
                        )
                        if member.scalar_one_or_none():
                            chain.append({
                                "type": "project",
                                "id": proj.id,
                                "label": proj.title,
                            })
                        else:
                            chain.append({"type": "redacted", "reason": "insufficient_access"})
                    else:
                        chain.append({"type": "redacted", "reason": "insufficient_access"})

        elif source_type == "rubric_score":
            from app.models.project import SubmissionReview

            review = await self.db.get(SubmissionReview, source_id)
            if review:
                # Check: requestor must be in the review's project org
                if requesting_user_id and hasattr(review, "submission_id"):
                    from app.models.project import Project
                    from app.models.project import Submission as SubModel

                    sub = await self.db.get(SubModel, review.submission_id) if review.submission_id else None
                    proj = await self.db.get(Project, sub.project_id) if sub and sub.project_id else None
                    if proj:


                        m = await self.db.execute(
                            select(OrgMember.id).where(OrgMember.org_id == proj.org_id, OrgMember.user_id == requesting_user_id).limit(1)
                        )
                        if m.scalar_one_or_none():
                            chain.append({"type": "submission_review", "id": review.id, "label": f"Review (score: {review.score})"})
                        else:
                            chain.append({"type": "redacted", "reason": "insufficient_access"})
                    else:
                        chain.append({"type": "submission_review", "id": review.id, "label": f"Review (score: {review.score})"})
                else:
                    chain.append({"type": "redacted", "reason": "insufficient_access"})

        elif source_type == "assessment_result":
            from app.talent.models.assessment import AssessmentRun

            run = await self.db.get(AssessmentRun, source_id)
            if run:
                # Check: requestor must be the run owner or in the run's org
                if requesting_user_id == run.user_id:
                    chain.append({"type": "assessment_run", "id": run.id, "label": f"Assessment (status: {run.status}, attempt #{run.attempt_number})"})
                elif requesting_user_id:


                    m = await self.db.execute(
                        select(OrgMember.id).where(OrgMember.org_id == run.org_id, OrgMember.user_id == requesting_user_id).limit(1)
                    )
                    if m.scalar_one_or_none():
                        chain.append({"type": "assessment_run", "id": run.id, "label": f"Assessment (status: {run.status}, attempt #{run.attempt_number})"})
                    else:
                        chain.append({"type": "redacted", "reason": "insufficient_access"})
                else:
                    chain.append({"type": "redacted", "reason": "insufficient_access"})

        elif source_type == "employment_verification":
            from app.talent.models.internship import EmployerVerification

            verif = await self.db.get(EmployerVerification, source_id)
            if verif:
                # Check: requestor must be the verified user or in the employer org
                if requesting_user_id == verif.user_id:
                    chain.append({"type": "employer_verification", "id": verif.id, "label": f"Employer verification (rating: {verif.overall_rating})"})
                elif requesting_user_id:


                    m = await self.db.execute(
                        select(OrgMember.id).where(OrgMember.org_id == verif.employer_org_id, OrgMember.user_id == requesting_user_id).limit(1)
                    )
                    if m.scalar_one_or_none():
                        chain.append({"type": "employer_verification", "id": verif.id, "label": f"Employer verification (rating: {verif.overall_rating})"})
                    else:
                        chain.append({"type": "redacted", "reason": "insufficient_access"})
                else:
                    chain.append({"type": "redacted", "reason": "insufficient_access"})

        elif source_type == "credential":
            from app.talent.models.assessment import Credential

            cred = await self.db.get(Credential, source_id)
            if cred:
                # Credentials are user-owned; requestor must be the owner
                if requesting_user_id == cred.user_id:
                    chain.append({"type": "credential", "id": cred.id, "label": f"{cred.credential_type} v{cred.version}"})
                else:
                    chain.append({"type": "redacted", "reason": "insufficient_access"})

        # skill_completion, exercise_result, peer_review, instructor_verification,
        # multimodal_ai_evaluation, client_acceptance, workflow_execution,
        # commercial_project_approval — single-hop (no deeper resolution needed;
        # the source_id points directly to the terminal record).

        return chain
