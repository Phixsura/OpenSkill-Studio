"""Creator matching from verified platform data (ADR-013, Issue #21 Part G).

Capability evidence is derived ONLY from platform-verified records (weight
1.0): completed skills, badges, approved submissions, commercial briefs,
completed workflow runs, evaluation results. The shortlist is an OFFER —
a human assigner offers, the creator accepts/declines. There is NO
auto-assignment path anywhere in this module (red line, R9).
"""

import structlog
from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.capability import CapabilityTag
from app.models.client_brief import ApplicationStatus, BriefApplication, ClientBrief
from app.models.composer import CreatorAssignment, CreatorCapabilityEvidence
from app.models.evaluation import EvalStatus, EvaluationTask
from app.models.organization import MemberStatus, OrgMember
from app.models.portfolio import SkillBadge
from app.models.project import ReviewStatus, Submission, SubmissionReview
from app.models.skill import ProgressStatus, Skill, SkillProgress
from app.models.workflow_run import RunStatus, WorkflowRun
from app.services.matching import MatchingEngine, MatchSpec
from app.services.requirement_profile import RequirementProfileService

log = structlog.get_logger()


class CreatorMatchingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Evidence derivation ───────────────────────────────

    async def _capability_keys(self) -> set[str]:
        result = await self.db.execute(select(CapabilityTag.key))
        return {row[0] for row in result.all()}

    @staticmethod
    def _map_tags(tags: list[str] | None, keys: set[str]) -> list[str]:
        """Map skill tags to capability keys (exact match after snake-casing)."""
        mapped = []
        for tag in tags or []:
            candidate = str(tag).strip().lower().replace(" ", "_").replace("-", "_")
            if candidate in keys:
                mapped.append(candidate)
        return mapped

    async def rebuild_evidence(self, org_id: str, user_id: str) -> int:
        """Idempotent per-user rebuild: delete + re-derive from verified sources."""
        keys = await self._capability_keys()
        await self.db.execute(
            sa_delete(CreatorCapabilityEvidence).where(
                CreatorCapabilityEvidence.org_id == org_id,
                CreatorCapabilityEvidence.user_id == user_id,
            )
        )
        rows: list[CreatorCapabilityEvidence] = []

        def add(capability: str, evidence_type: str, evidence_id: str, occurred_at, score=None):
            rows.append(
                CreatorCapabilityEvidence(
                    org_id=org_id,
                    user_id=user_id,
                    capability_key=capability,
                    evidence_type=evidence_type,
                    evidence_id=evidence_id,
                    weight=1.0,  # platform-verified
                    score=score,
                    occurred_at=occurred_at,
                )
            )

        # 1. Completed skills (tags → capabilities)
        sp_r = await self.db.execute(
            select(SkillProgress, Skill)
            .join(Skill, Skill.id == SkillProgress.skill_id)
            .where(
                Skill.org_id == org_id,
                SkillProgress.user_id == user_id,
                SkillProgress.status == ProgressStatus.COMPLETED,
            )
        )
        for progress, skill in sp_r.all():
            score = None
            if progress.best_score is not None:
                score = min(progress.best_score / 100.0, 1.0)
            for cap in self._map_tags(list(skill.tags or []), keys):
                add(cap, "skill_completed", progress.id, progress.completed_at or progress.started_at or skill.created_at, score)

        # 2. Skill badges
        badge_r = await self.db.execute(
            select(SkillBadge, Skill)
            .join(Skill, Skill.id == SkillBadge.skill_id)
            .where(SkillBadge.org_id == org_id, SkillBadge.user_id == user_id)
        )
        for badge, skill in badge_r.all():
            for cap in self._map_tags(list(skill.tags or []), keys):
                add(cap, "badge", badge.id, badge.completed_at or badge.created_at)

        # 3. Approved submission reviews (capability from project_type)
        rev_r = await self.db.execute(
            select(SubmissionReview, Submission)
            .join(Submission, Submission.id == SubmissionReview.submission_id)
            .where(
                Submission.org_id == org_id,
                Submission.user_id == user_id,
                SubmissionReview.status == ReviewStatus.APPROVED,
            )
        )
        for review, submission in rev_r.all():
            from app.models.project import Project as _Project

            project = await self.db.get(_Project, submission.project_id)
            cap = (project.project_type or "").strip().lower() if project else ""
            if cap in keys:
                score = min((review.score or 0) / 100.0, 1.0) if review.score is not None else None
                add(cap, "approved_submission", review.id, review.created_at, score)

        # 4. Accepted commercial brief applications
        app_r = await self.db.execute(
            select(BriefApplication, ClientBrief)
            .join(ClientBrief, ClientBrief.id == BriefApplication.brief_id)
            .where(
                ClientBrief.org_id == org_id,
                BriefApplication.user_id == user_id,
                BriefApplication.status == ApplicationStatus.ACCEPTED,
            )
        )
        for application, brief in app_r.all():
            cap = (brief.project_type or "").strip().lower()
            if cap in keys:
                add(cap, "commercial_project", application.id, application.reviewed_at or application.applied_at)

        # 5. Completed workflow runs (capabilities from provider_action steps)
        run_r = await self.db.execute(
            select(WorkflowRun).where(
                WorkflowRun.org_id == org_id,
                WorkflowRun.started_by == user_id,
                WorkflowRun.status == RunStatus.COMPLETED,
            )
        )
        for run in run_r.scalars().all():
            caps = {
                s.get("config", {}).get("capability", "")
                for s in (run.definition_snapshot or {}).get("steps", [])
                if s.get("type") == "provider_action"
            }
            for cap in sorted(c for c in caps if c in keys):
                add(cap, "workflow_run", run.id, run.finished_at or run.created_at)

        # 6. Completed evaluation results (capability via submission's project_type)
        eval_r = await self.db.execute(
            select(EvaluationTask, Submission)
            .join(Submission, Submission.id == EvaluationTask.submission_id)
            .where(
                EvaluationTask.org_id == org_id,
                Submission.user_id == user_id,
                EvaluationTask.status == EvalStatus.COMPLETED,
                EvaluationTask.result.isnot(None),
            )
        )
        for task, submission in eval_r.all():
            from app.models.project import Project as _Project

            project = await self.db.get(_Project, submission.project_id)
            cap = (project.project_type or "").strip().lower() if project else ""
            if cap in keys:
                raw = task.result.get("overall_score", task.result.get("score"))
                score = None
                if isinstance(raw, int | float):
                    score = min(float(raw) / 100.0, 1.0)
                add(cap, "eval_result", task.id, task.completed_at or task.created_at, score)

        for row in rows:
            self.db.add(row)
        await self.db.flush()
        return len(rows)

    async def rebuild_org_evidence(self, org_id: str) -> int:
        members_r = await self.db.execute(
            select(OrgMember.user_id).where(
                OrgMember.org_id == org_id, OrgMember.status == MemberStatus.ACTIVE
            )
        )
        total = 0
        for (user_id,) in members_r.all():
            total += await self.rebuild_evidence(org_id, user_id)
        return total

    # ── Shortlist (offer, never assign) ───────────────────

    async def shortlist(
        self, org_id: str, project_id: str, profile_id: str, created_by: str, limit: int = 10
    ):
        from app.models.project import Project as _Project

        project = await self.db.get(_Project, project_id)
        if project is None or project.org_id != org_id:
            raise AppError("PROJECT_NOT_FOUND", "Project not found", 404)

        profile_svc = RequirementProfileService(self.db)
        profile = await profile_svc.get_profile(profile_id, org_id)
        if profile.status != "confirmed":
            raise AppError(
                "PROFILE_NOT_CONFIRMED",
                "Requirement profile must be confirmed before shortlisting",
                422,
            )

        # Fresh evidence for the whole org before ranking
        await self.rebuild_org_evidence(org_id)

        requirement = RequirementProfileService.build_match_requirement(profile)
        engine = MatchingEngine(self.db)
        run, results, _ = await engine.run(
            MatchSpec(
                org_id=org_id,
                target_entity_type="creator",
                requirement=requirement,
                context_type=profile.context_type.value,
                requirement_profile_id=profile.id,
                created_by=created_by,
                limit=limit,
            )
        )

        # Attach grouped evidence detail to ranked creators
        ranked_ids = [r.entity_id for r in results if r.rank is not None]
        evidence_by_user: dict[str, dict[str, list[dict]]] = {}
        if ranked_ids:
            ev_r = await self.db.execute(
                select(CreatorCapabilityEvidence).where(
                    CreatorCapabilityEvidence.org_id == org_id,
                    CreatorCapabilityEvidence.user_id.in_(ranked_ids),
                )
            )
            for ev in ev_r.scalars().all():
                by_cap = evidence_by_user.setdefault(ev.user_id, {})
                by_cap.setdefault(ev.capability_key, []).append(
                    {
                        "evidence_type": ev.evidence_type,
                        "score": float(ev.score) if ev.score is not None else None,
                        "occurred_at": ev.occurred_at.isoformat() if ev.occurred_at else None,
                    }
                )
        return run, results, evidence_by_user

    # ── Assignment offers (human decision, both sides) ────

    async def offer_assignment(
        self,
        org_id: str,
        project_id: str,
        user_id: str,
        assigned_by: str,
        match_run_id: str | None = None,
        override_reason: str | None = None,
    ) -> CreatorAssignment:
        from app.models.project import Project as _Project

        project = await self.db.get(_Project, project_id)
        if project is None or project.org_id != org_id:
            raise AppError("PROJECT_NOT_FOUND", "Project not found", 404)
        member_r = await self.db.execute(
            select(OrgMember).where(
                OrgMember.org_id == org_id,
                OrgMember.user_id == user_id,
                OrgMember.status == MemberStatus.ACTIVE,
            )
        )
        if member_r.scalar_one_or_none() is None:
            raise AppError("NOT_A_MEMBER", "User is not an active member of this organization", 422)

        assignment = CreatorAssignment(
            org_id=org_id,
            project_id=project_id,
            user_id=user_id,
            match_run_id=match_run_id,
            assigned_by=assigned_by,  # always a human user (R9)
            override_reason=override_reason,
        )
        try:
            async with self.db.begin_nested():
                self.db.add(assignment)
                await self.db.flush()
        except IntegrityError:
            raise AppError(
                "ASSIGNMENT_EXISTS", "This creator already has an offer for this project", 409
            ) from None
        log.info(
            "creator_assignment_offered",
            project_id=project_id,
            user_id=user_id,
            assigned_by=assigned_by,
        )
        return assignment

    async def respond_assignment(
        self, assignment_id: str, org_id: str, user_id: str, accept: bool
    ) -> CreatorAssignment:
        from datetime import UTC, datetime

        assignment = await self.db.get(CreatorAssignment, assignment_id)
        if assignment is None or assignment.org_id != org_id:
            raise AppError("ASSIGNMENT_NOT_FOUND", "Assignment not found", 404)
        if assignment.user_id != user_id:
            raise AppError("NOT_YOUR_ASSIGNMENT", "Only the offered creator can respond", 403)
        if assignment.status != "offered":
            raise AppError("ALREADY_RESPONDED", "This offer was already responded to", 409)
        assignment.status = "accepted" if accept else "declined"
        assignment.responded_at = datetime.now(UTC)
        await self.db.flush()
        return assignment

    async def list_assignments(
        self, org_id: str, project_id: str | None = None
    ) -> list[CreatorAssignment]:
        query = select(CreatorAssignment).where(CreatorAssignment.org_id == org_id)
        if project_id:
            query = query.where(CreatorAssignment.project_id == project_id)
        result = await self.db.execute(query.order_by(CreatorAssignment.created_at.desc()))
        return list(result.scalars().all())
