"""Creator matching from verified platform data (ADR-013, Issue #21 Part G).

Capability evidence is derived ONLY from platform-verified records (weight
1.0): completed skills, badges, approved submissions, commercial briefs,
completed workflow runs, evaluation results. The shortlist is an OFFER —
a human assigner offers, the creator accepts/declines. There is NO
auto-assignment path anywhere in this module (red line, R9).
"""

import structlog
from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.capability import CapabilityTag
from app.models.client_brief import ApplicationStatus, BriefApplication, ClientBrief
from app.models.composer import CreatorAssignment, CreatorCapabilityEvidence
from app.models.evaluation import EvalStatus, EvaluationTask
from app.models.organization import MemberStatus, OrgMember
from app.models.portfolio import SkillBadge
from app.models.project import ReviewStatus, Submission, SubmissionReview, SubmissionStatus
from app.models.skill import ContentStatus, Exercise, ProgressStatus, Skill, SkillProgress
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

    async def _load_projects(self, project_ids: set[str]) -> dict:
        """Batch-load projects by id (avoids per-row db.get N+1)."""
        from app.models.project import Project as _Project

        ids = {pid for pid in project_ids if pid}
        if not ids:
            return {}
        result = await self.db.execute(select(_Project).where(_Project.id.in_(ids)))
        return {p.id: p for p in result.scalars().all()}

    @staticmethod
    def _norm_cap(value) -> str:
        """Normalize free text toward a capability key (snake-casing)."""
        return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")

    @classmethod
    def _map_tags(cls, tags: list[str] | None, keys: set[str]) -> list[str]:
        """Map skill tags to capability keys (exact match after snake-casing)."""
        mapped = []
        for tag in tags or []:
            candidate = cls._norm_cap(tag)
            if candidate in keys:
                mapped.append(candidate)
        return mapped

    async def _project_capabilities(
        self, projects_by_id: dict, keys: set[str]
    ) -> dict[str, list[str]]:
        """Resolve each project to the capability keys its work attests.

        project.project_type is a coarse UX taxonomy ({general, ai_visual})
        that never intersects capability keys, so on its own it can never
        attest a capability. The real signals, checked in order per project:
          1. project.project_type itself (future-proof, currently never hits),
          2. the linked client brief's project_type (free text — counts only
             when it normalizes to an exact capability key),
          3. the confirmed production-solution draft that materialized the
             project (payload.required_capabilities — the platform-verified
             capability rollup from workflow release manifests).
        Both lookups are batched (no per-project queries).
        """
        caps_by_project: dict[str, list[str]] = {}
        if not projects_by_id:
            return caps_by_project

        brief_ids = {
            p.client_brief_id for p in projects_by_id.values() if p.client_brief_id
        }
        briefs_by_id: dict[str, ClientBrief] = {}
        if brief_ids:
            brief_r = await self.db.execute(
                select(ClientBrief).where(ClientBrief.id.in_(brief_ids))
            )
            briefs_by_id = {b.id: b for b in brief_r.scalars().all()}

        from app.models.composer import SolutionDraft

        draft_r = await self.db.execute(
            select(SolutionDraft).where(
                SolutionDraft.draft_type == "production_solution",
                SolutionDraft.status == "confirmed",
                SolutionDraft.materialized_entity_id.in_(set(projects_by_id)),
            )
        )
        draft_caps: dict[str, list[str]] = {}
        for draft in draft_r.scalars().all():
            raw = (draft.payload or {}).get("required_capabilities", [])
            for cap in raw if isinstance(raw, list) else []:
                key = cap.get("capability", "") if isinstance(cap, dict) else ""
                if isinstance(key, str) and key:
                    draft_caps.setdefault(draft.materialized_entity_id, []).append(key)

        for pid, project in projects_by_id.items():
            ordered: list[str] = []
            candidates = [project.project_type]
            brief = briefs_by_id.get(project.client_brief_id or "")
            if brief:
                candidates.append(brief.project_type)
            candidates.extend(draft_caps.get(pid, []))
            for raw_cap in candidates:
                cap = self._norm_cap(raw_cap)
                if cap in keys and cap not in ordered:
                    ordered.append(cap)
            caps_by_project[pid] = ordered
        return caps_by_project

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
        progress_rows = sp_r.all()
        # SkillProgress.best_score is the SUM of best attempt scores across
        # the skill's ACTIVE exercises (skill.py _update_skill_progress via
        # list_exercises, which filters ARCHIVED), each on that exercise's
        # own max_score scale (1..10000, API-settable). Correct normalization
        # is sum(best) / sum(active max_score) — a count-based denominator
        # would under-report skills with archived exercises and misprice any
        # exercise whose max_score isn't 100. Stored evidence scores are on
        # the 0-100 scale (Numeric(5,2)); scoring.py normalizes to 0-1 once
        # at read time.
        skill_ids = {skill.id for _, skill in progress_rows}
        max_score_sums: dict[str, int] = {}
        if skill_ids:
            ex_r = await self.db.execute(
                select(Exercise.skill_id, func.sum(Exercise.max_score))
                .where(
                    Exercise.skill_id.in_(skill_ids),
                    Exercise.status != ContentStatus.ARCHIVED,
                )
                .group_by(Exercise.skill_id)
            )
            max_score_sums = {row[0]: int(row[1] or 0) for row in ex_r.all()}
        for progress, skill in progress_rows:
            score = None
            if progress.best_score is not None:
                denom = max_score_sums.get(skill.id, 0)
                score = min(
                    float(progress.best_score) / max(1, denom) * 100.0, 100.0
                )
            for cap in self._map_tags(list(skill.tags or []), keys):
                add(cap, "skill_completed", progress.id, progress.completed_at or progress.started_at or skill.created_at, score)

        # 2. Skill badges
        badge_r = await self.db.execute(
            select(SkillBadge, Skill)
            .join(Skill, Skill.id == SkillBadge.skill_id)
            .where(SkillBadge.org_id == org_id, SkillBadge.user_id == user_id)
        )
        for badge, skill in badge_r.all():
            # A SkillBadge row is created/updated on ANY progress
            # (completion_pct = exercises_done/total), so a badge at 20% —
            # or one earned by auto-graded wrong MCQ attempts — exists long
            # before the skill is mastered. Only a FULLY completed badge
            # (100%) is capability evidence; a partial badge attests nothing.
            if (badge.completion_pct or 0) < 100:
                continue
            for cap in self._map_tags(list(skill.tags or []), keys):
                add(cap, "badge", badge.id, badge.completed_at or badge.created_at)

        # 3. Approved submission reviews (capability via project resolution:
        # project_type → linked brief → confirmed production draft — see
        # _project_capabilities; bare project_type never matches a key)
        # R92g: also require the SUBMISSION's FINAL status to be APPROVED, not
        # just that some review row is APPROVED. A submission can be approved and
        # then reopened (revision_requested) or flipped to rejected — a stale
        # APPROVED review row lingers, and counting it kept crediting verified
        # creator evidence for work whose current state is NOT approved. Gate on
        # the live submission status so evidence tracks the settled outcome.
        rev_r = await self.db.execute(
            select(SubmissionReview, Submission)
            .join(Submission, Submission.id == SubmissionReview.submission_id)
            .where(
                Submission.org_id == org_id,
                Submission.user_id == user_id,
                SubmissionReview.status == ReviewStatus.APPROVED,
                Submission.status == SubmissionStatus.APPROVED,
            )
        )
        review_rows = rev_r.all()
        # R92: a submission can accumulate MORE THAN ONE approved review over its
        # lifetime (re-review / grade correction is an allowed instructor action).
        # Keying evidence on review.id would then mint one weight-1.0
        # approved_submission row PER review — an instructor could inflate a
        # creator's verified evidence without bound simply by re-approving the
        # same submission. Collapse to the LATEST approved review per submission
        # (evidence is "this submission was approved", counted once), so the
        # evidence is idempotent in the work, not in the number of review clicks.
        latest_by_submission: dict[str, object] = {}
        submissions_by_id: dict[str, object] = {}
        for review, submission in review_rows:
            submissions_by_id[submission.id] = submission
            prev = latest_by_submission.get(submission.id)
            if prev is None or review.created_at > prev.created_at:
                latest_by_submission[submission.id] = review
        review_project_ids = {s.project_id for s in submissions_by_id.values()}
        projects_by_id = await self._load_projects(review_project_ids)
        review_caps = await self._project_capabilities(projects_by_id, keys)
        for submission_id, review in latest_by_submission.items():
            submission = submissions_by_id[submission_id]
            project = projects_by_id.get(submission.project_id)
            for cap in review_caps.get(submission.project_id, []):
                # SubmissionReview.score is on the PROJECT's max_score scale
                # (validated against project.max_score, which may be 10 or
                # 10000) — rescale to 0-100 before storing so evidence scores
                # are comparable across projects.
                score = None
                if review.score is not None:
                    max_score = project.max_score if project and project.max_score else 100
                    score = min(float(review.score) / max(max_score, 1) * 100.0, 100.0)
                # Evidence id is the SUBMISSION, not the review row, so repeated
                # approvals of the same work stay a single evidence record.
                add(cap, "approved_submission", submission_id, review.created_at, score)

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
            # Same snake-case normalization as skill tags — "Image Generation"
            # in a free-text brief field should attest image_generation.
            cap = self._norm_cap(brief.project_type)
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

        # 6. Completed evaluation results (capability via the same project
        # resolution as source 3)
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
        eval_rows = eval_r.all()
        eval_project_ids = {submission.project_id for _, submission in eval_rows}
        eval_projects_by_id = await self._load_projects(eval_project_ids)
        eval_caps = await self._project_capabilities(eval_projects_by_id, keys)
        for task, submission in eval_rows:
            for cap in eval_caps.get(submission.project_id, []):
                # EvaluationService stores {total_score, max_score, scores,
                # ...} (evaluation._parse_evaluation_response). The keys read
                # before ("overall_score"/"score") never exist, so score was
                # ALWAYS None → every eval_result row scored as bare 1.0*weight
                # in Bayesian shrinkage, discarding the actual grade. Rescale
                # total_score by its max_score to the 0-100 evidence scale
                # (max_score varies with the rubric, like SubmissionReview).
                raw = task.result.get("total_score")
                raw_max = task.result.get("max_score")
                score = None
                if isinstance(raw, int | float) and isinstance(raw_max, int | float):
                    score = min(float(raw) / max(float(raw_max), 1.0) * 100.0, 100.0)
                elif isinstance(raw, int | float):
                    # No max recorded — fall back to clamping the raw value
                    score = min(float(raw), 100.0)
                add(cap, "eval_result", task.id, task.completed_at or task.created_at, score)

        for row in rows:
            self.db.add(row)
        await self.db.flush()
        return len(rows)

    # Evidence younger than this is considered fresh enough for shortlisting;
    # callers pass force=True to bypass (e.g. an explicit refresh action).
    EVIDENCE_STALENESS_SECONDS = 600

    async def rebuild_org_evidence(self, org_id: str, force: bool = False) -> int:
        """Rebuild evidence for all active members.

        Skipped (returns 0) when existing evidence is fresh and force is
        False — shortlisting is a read path and must not mass-rewrite the
        evidence table on every request (N+1 + lock contention).

        A transaction-scoped Postgres advisory lock serializes concurrent
        rebuilds: without it, two requests both pass the read-then-act
        staleness gate, both run delete+re-insert, and (READ COMMITTED —
        neither DELETE sees the other's uncommitted inserts) every evidence
        row ends up duplicated. The second rebuild blocks on the lock, then
        re-checks staleness against the winner's fresh rows and skips.
        """
        from sqlalchemy import text as sa_text

        # Advisory lock FIRST (auto-released at transaction end), then the
        # staleness check — checking before the lock reintroduces the race.
        # The lock must cover ONLY the staleness-check + delete/insert window:
        # xact-scoped locks otherwise ride along to the endpoint's commit,
        # serializing every same-org shortlist request behind the full
        # matching-engine run. Committing here releases the lock the moment
        # the rebuild (idempotent rows, safe to commit early) is durable —
        # expire_on_commit=False keeps loaded objects usable.
        await self.db.execute(
            sa_text("SELECT pg_advisory_xact_lock(hashtext('evidence:' || :org_id))"),
            {"org_id": org_id},
        )
        try:
            if not force:
                from datetime import UTC, datetime, timedelta

                newest_r = await self.db.execute(
                    select(func.max(CreatorCapabilityEvidence.created_at)).where(
                        CreatorCapabilityEvidence.org_id == org_id
                    )
                )
                newest = newest_r.scalar_one_or_none()
                if newest is not None:
                    ref = newest if newest.tzinfo else newest.replace(tzinfo=UTC)
                    if datetime.now(UTC) - ref < timedelta(
                        seconds=self.EVIDENCE_STALENESS_SECONDS
                    ):
                        # Fresh enough — release the lock before returning
                        # (commit ends the lock-holding transaction; nothing
                        # was written, so committing is a no-op data-wise)
                        await self.db.commit()
                        return 0

            members_r = await self.db.execute(
                select(OrgMember.user_id).where(
                    OrgMember.org_id == org_id, OrgMember.status == MemberStatus.ACTIVE
                )
            )
            total = 0
            for (user_id,) in members_r.all():
                total += await self.rebuild_evidence(org_id, user_id)
        except BaseException:
            # Rollback discards the partial delete+insert AND releases the
            # advisory lock (transaction end) — never commit half a rebuild.
            await self.db.rollback()
            raise
        else:
            # Commit releases the advisory lock the moment the rebuild is
            # durable (fresh-skip path included via the return above — see
            # the early-return commit below). Holding an xact lock through
            # the endpoint's own commit would serialize every same-org
            # shortlist behind the full matching-engine run.
            await self.db.commit()
            return total

    # ── Shortlist (offer, never assign) ───────────────────

    async def shortlist(
        self,
        org_id: str,
        project_id: str,
        profile_id: str,
        created_by: str,
        limit: int = 10,
        force_refresh: bool = False,
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

        # Evidence refresh, staleness-gated (skipped when <10 min old unless
        # the caller explicitly forces a refresh)
        await self.rebuild_org_evidence(org_id, force=force_refresh)

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
        # Same guard as respond_assignment's accept branch: offering against
        # an archived project manufactures a dead offer the creator can never
        # accept (and the unique index then blocks any future re-offer)
        if project.status == ContentStatus.ARCHIVED:
            raise AppError(
                "PROJECT_NOT_AVAILABLE", "Project is archived — offers are closed", 409
            )
        # match_run_id is a loose (non-FK) reference — validate org ownership
        # the same way feedback-events does (ADR-012), or an over-length /
        # cross-org value 500s or silently attaches a foreign run.
        if match_run_id is not None:
            from app.models.matching import MatchRun

            run = await self.db.get(MatchRun, match_run_id)
            if run is None or run.org_id != org_id:
                raise AppError("MATCH_RUN_NOT_FOUND", "Match run not found", 404)
        member_r = await self.db.execute(
            select(OrgMember).where(
                OrgMember.org_id == org_id,
                OrgMember.user_id == user_id,
                OrgMember.status == MemberStatus.ACTIVE,
            )
        )
        if member_r.scalar_one_or_none() is None:
            raise AppError("NOT_A_MEMBER", "User is not an active member of this organization", 422)

        # uq_creator_assignment is unconditional on (project_id, user_id), so
        # a prior DECLINED/WITHDRAWN offer would permanently block re-offering
        # this creator — an instructor could never revisit someone who once
        # declined (or was withdrawn). A resolved (non-active) prior offer is
        # superseded IN PLACE with a fresh offer; only a still-'offered' or
        # 'accepted' row is a real conflict (409).
        existing_r = await self.db.execute(
            select(CreatorAssignment).where(
                CreatorAssignment.project_id == project_id,
                CreatorAssignment.user_id == user_id,
            )
        )
        existing = existing_r.scalar_one_or_none()
        if existing is not None:
            if existing.status in ("offered", "accepted"):
                raise AppError(
                    "ASSIGNMENT_EXISTS",
                    "This creator already has an active offer for this project",
                    409,
                )
            # declined/withdrawn → re-open the SAME row as a new offer
            reopened = await self.db.execute(
                update(CreatorAssignment)
                .where(
                    CreatorAssignment.id == existing.id,
                    CreatorAssignment.status.in_(("declined", "withdrawn")),
                )
                .values(
                    status="offered",
                    match_run_id=match_run_id,
                    assigned_by=assigned_by,
                    override_reason=override_reason,
                    responded_at=None,
                )
            )
            if not reopened.rowcount:
                # Lost a race to a concurrent re-offer/response
                raise AppError(
                    "ASSIGNMENT_EXISTS",
                    "This creator already has an active offer for this project",
                    409,
                )
            await self.db.refresh(existing)
            log.info(
                "creator_assignment_reoffered",
                project_id=project_id,
                user_id=user_id,
                assigned_by=assigned_by,
            )
            return existing

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
            raise AppError(
                "ASSIGNMENT_ALREADY_RESPONDED", "This offer was already responded to", 409
            )
        if accept:
            # Projects are soft-deleted (status=ARCHIVED), so open offers
            # survive archival — a creator must not accept a dead project.
            from app.models.project import Project as _Project
            from app.models.skill import ContentStatus as _ContentStatus

            project = await self.db.get(_Project, assignment.project_id)
            if project is None or project.status == _ContentStatus.ARCHIVED:
                raise AppError(
                    "PROJECT_NOT_AVAILABLE",
                    "The project for this offer is no longer available",
                    409,
                )
        # Conditional UPDATE guards the read-check-write race: two concurrent
        # responds both pass the status read above, but only ONE wins the
        # status-guarded UPDATE — the loser's rowcount is 0 → 409 (same
        # pattern as claim_draft_for_confirm).
        result = await self.db.execute(
            update(CreatorAssignment)
            .where(
                CreatorAssignment.id == assignment_id,
                CreatorAssignment.status == "offered",
            )
            .values(
                status="accepted" if accept else "declined",
                responded_at=datetime.now(UTC),
            )
        )
        if result.rowcount == 0:
            raise AppError(
                "ASSIGNMENT_ALREADY_RESPONDED", "This offer was already responded to", 409
            )
        await self.db.refresh(assignment)
        return assignment

    async def withdraw_assignment(
        self, assignment_id: str, org_id: str
    ) -> CreatorAssignment:
        """Assigner-side retraction of a pending offer.

        Completes the state machine offer_assignment already supersedes on
        ('declined'/'withdrawn' rows are re-openable): without this, a
        mis-directed offer is irrevocable by the instructor — it blocks any
        re-offer via ASSIGNMENT_EXISTS until the creator happens to decline.
        Only a still-pending 'offered' row can be withdrawn; an accepted or
        declined offer already resolved (409).
        """
        from datetime import UTC, datetime

        assignment = await self.db.get(CreatorAssignment, assignment_id)
        if assignment is None or assignment.org_id != org_id:
            raise AppError("ASSIGNMENT_NOT_FOUND", "Assignment not found", 404)
        # Conditional UPDATE: a concurrent accept/decline may resolve the
        # offer between the read and this write — the loser gets rowcount 0
        # (same race guard as respond_assignment).
        result = await self.db.execute(
            update(CreatorAssignment)
            .where(
                CreatorAssignment.id == assignment_id,
                CreatorAssignment.status == "offered",
            )
            .values(status="withdrawn", responded_at=datetime.now(UTC))
        )
        if result.rowcount == 0:
            raise AppError(
                "ASSIGNMENT_ALREADY_RESPONDED", "This offer was already responded to", 409
            )
        await self.db.refresh(assignment)
        log.info(
            "creator_assignment_withdrawn",
            assignment_id=assignment_id,
            org_id=org_id,
        )
        return assignment

    async def list_assignments(
        self,
        org_id: str,
        project_id: str | None = None,
        only_user_id: str | None = None,
    ) -> list[CreatorAssignment]:
        """List assignments; only_user_id scopes to one creator's own offers.

        Non-instructor members must pass only_user_id=their id — an
        unscoped list exposes every creator's offer/decline history and the
        assigner's override_reason (recorded discretion, ADR-013) to any
        student in the org.
        """
        query = select(CreatorAssignment).where(CreatorAssignment.org_id == org_id)
        if project_id:
            query = query.where(CreatorAssignment.project_id == project_id)
        if only_user_id:
            query = query.where(CreatorAssignment.user_id == only_user_id)
        result = await self.db.execute(query.order_by(CreatorAssignment.created_at.desc(), CreatorAssignment.id.desc()))
        return list(result.scalars().all())
