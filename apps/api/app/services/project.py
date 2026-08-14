"""Project, submission, review, and file upload service."""

import re
import secrets
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.config import settings
from app.exceptions import AppError
from app.models.project import (
    DeliverableType,
    ItemType,
    Project,
    ProjectDeliverable,
    ProjectSkill,
    ReviewerType,
    ReviewStatus,
    Submission,
    SubmissionExtension,
    SubmissionItem,
    SubmissionReview,
    SubmissionStatus,
)
from app.models.skill import ContentStatus, DifficultyLevel

log = structlog.get_logger()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ── Errors ────────────────────────────────────────────────────


class ProjectNotFoundError(AppError):
    def __init__(self):
        super().__init__("PROJECT_NOT_FOUND", "Project not found", 404)


class DeliverableNotFoundError(AppError):
    def __init__(self):
        super().__init__("DELIVERABLE_NOT_FOUND", "Deliverable not found", 404)


class SubmissionNotFoundError(AppError):
    def __init__(self):
        super().__init__("SUBMISSION_NOT_FOUND", "Submission not found", 404)


class MaxSubmissionsReachedError(AppError):
    def __init__(self, limit: int):
        super().__init__("MAX_SUBMISSIONS_REACHED", f"Maximum of {limit} submissions reached", 422)


class DeadlinePassedError(AppError):
    def __init__(self):
        super().__init__("DEADLINE_PASSED", "Submission deadline has passed", 422)


class InvalidStateError(AppError):
    def __init__(self, detail: str = "Invalid submission state"):
        super().__init__("INVALID_STATE", detail, 422)


class MissingDeliverablesError(AppError):
    def __init__(self):
        super().__init__("MISSING_DELIVERABLES", "Required deliverables are missing", 422)


class FileTooLargeError(AppError):
    def __init__(self):
        super().__init__(
            "FILE_TOO_LARGE",
            f"File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)}MB",
            413,
        )


# ── Service ───────────────────────────────────────────────────


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Project CRUD ──

    async def create_project(
        self,
        org_id: str,
        title: str,
        slug: str | None,
        description: str,
        instructions: str,
        difficulty: str,
        max_score: int,
        rubric: list[dict],
        deadline: datetime | None,
        late_deadline: datetime | None,
        late_penalty_pct: int,
        max_submissions: int,
        skill_ids: list[str] | None,
        created_by: str,
    ) -> Project:
        if slug is None:
            slug = self._generate_slug(title)

        try:
            diff = DifficultyLevel(difficulty)
        except ValueError:
            diff = DifficultyLevel.INTERMEDIATE

        project = Project(
            org_id=org_id,
            title=title,
            slug=slug,
            description=description,
            instructions=instructions,
            difficulty=diff,
            max_score=max_score,
            rubric=rubric,
            deadline=deadline,
            late_deadline=late_deadline,
            late_penalty_pct=late_penalty_pct,
            max_submissions=max_submissions,
            created_by=created_by,
        )
        self.db.add(project)
        await self.db.flush()

        if skill_ids:
            await self._set_project_skills(project.id, skill_ids)

        log.info("project_created", project_id=project.id, org_id=org_id)
        return project

    async def list_projects(
        self,
        org_id: str,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Project], int]:
        base = select(Project).where(Project.org_id == org_id)
        if status:
            base = base.where(Project.status == ContentStatus(status))
        else:
            base = base.where(Project.status != ContentStatus.ARCHIVED)

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()

        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(Project.deadline.asc().nulls_last(), Project.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_project(self, project_id: str) -> Project:
        project = await self.db.get(Project, project_id)
        if project is None or project.status == ContentStatus.ARCHIVED:
            raise ProjectNotFoundError()
        return project

    async def update_project(self, project_id: str, **fields) -> Project:
        project = await self.get_project(project_id)
        for k, v in fields.items():
            if v is not None and hasattr(project, k):
                if k == "difficulty":
                    v = DifficultyLevel(v)
                setattr(project, k, v)
        await self.db.flush()
        return project

    async def delete_project(self, project_id: str) -> None:
        project = await self.get_project(project_id)
        project.status = ContentStatus.ARCHIVED
        await self.db.flush()

    async def publish_project(self, project_id: str) -> Project:
        project = await self.get_project(project_id)
        project.status = ContentStatus.PUBLISHED
        project.published_at = datetime.now(UTC)
        await self.db.flush()
        return project

    async def unpublish_project(self, project_id: str) -> Project:
        project = await self.get_project(project_id)
        project.status = ContentStatus.DRAFT
        await self.db.flush()
        return project

    async def set_project_skills(self, project_id: str, skill_ids: list[str]) -> None:
        await self._set_project_skills(project_id, skill_ids)
        await self.db.flush()

    async def get_project_skill_ids(self, project_id: str) -> list[str]:
        result = await self.db.execute(
            select(ProjectSkill.skill_id).where(ProjectSkill.project_id == project_id)
        )
        return list(result.scalars().all())

    # ── Deliverables ──

    async def create_deliverable(
        self,
        project_id: str,
        name: str,
        description: str | None,
        deliverable_type: str,
        required: bool,
        config: dict,
        sort_order: int,
    ) -> ProjectDeliverable:
        try:
            dtype = DeliverableType(deliverable_type)
        except ValueError as exc:
            raise AppError(
                "INVALID_TYPE", f"Invalid deliverable type: {deliverable_type}", 422
            ) from exc

        deliverable = ProjectDeliverable(
            project_id=project_id,
            name=name,
            description=description,
            type=dtype,
            required=required,
            config=config,
            sort_order=sort_order,
        )
        self.db.add(deliverable)
        await self.db.flush()
        return deliverable

    async def list_deliverables(self, project_id: str) -> list[ProjectDeliverable]:
        result = await self.db.execute(
            select(ProjectDeliverable)
            .where(ProjectDeliverable.project_id == project_id)
            .order_by(ProjectDeliverable.sort_order)
        )
        return list(result.scalars().all())

    async def get_deliverable(self, deliverable_id: str) -> ProjectDeliverable:
        d = await self.db.get(ProjectDeliverable, deliverable_id)
        if d is None:
            raise DeliverableNotFoundError()
        return d

    async def update_deliverable(self, deliverable_id: str, **fields) -> ProjectDeliverable:
        d = await self.db.get(ProjectDeliverable, deliverable_id)
        if d is None:
            raise DeliverableNotFoundError()
        for k, v in fields.items():
            if v is not None and hasattr(d, k):
                setattr(d, k, v)
        await self.db.flush()
        return d

    async def delete_deliverable(self, deliverable_id: str) -> None:
        d = await self.db.get(ProjectDeliverable, deliverable_id)
        if d is None:
            raise DeliverableNotFoundError()
        await self.db.delete(d)
        await self.db.flush()

    # ── Submissions ──

    async def create_submission(
        self,
        org_id: str,
        project_id: str,
        user_id: str,
    ) -> Submission:
        project = await self.get_project(project_id)
        count = await self._count_user_submissions(project_id, user_id)

        if project.max_submissions > 0 and count >= project.max_submissions:
            raise MaxSubmissionsReachedError(project.max_submissions)

        submission = Submission(
            org_id=org_id,
            project_id=project_id,
            user_id=user_id,
            version=count + 1,
            status=SubmissionStatus.DRAFT,
        )
        self.db.add(submission)
        await self.db.flush()
        return submission

    async def get_submission(self, submission_id: str) -> Submission:
        sub = await self.db.get(Submission, submission_id)
        if sub is None:
            raise SubmissionNotFoundError()
        return sub

    async def list_submissions(
        self,
        project_id: str,
        user_id: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Submission], int]:
        base = select(Submission).where(Submission.project_id == project_id)
        if user_id:
            base = base.where(Submission.user_id == user_id)

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()

        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(Submission.version.desc()).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    async def submit_draft(self, submission_id: str, user_id: str) -> Submission:
        sub = await self.get_submission(submission_id)

        if sub.user_id != user_id:
            raise AppError("PERMISSION_DENIED", "Not your submission", 403)
        if sub.status != SubmissionStatus.DRAFT:
            raise InvalidStateError("Only drafts can be submitted")

        # Check required deliverables
        await self._validate_required_deliverables(sub)

        # Check deadline
        project = await self.get_project(sub.project_id)
        timing = await self.get_submission_timing(project, user_id)
        if timing == "closed":
            raise DeadlinePassedError()

        sub.status = SubmissionStatus.SUBMITTED
        sub.submitted_at = datetime.now(UTC)
        sub.is_late = timing == "late"
        await self.db.flush()

        log.info(
            "submission_submitted", submission_id=sub.id, version=sub.version, is_late=sub.is_late
        )
        return sub

    async def delete_submission(self, submission_id: str, user_id: str) -> None:
        sub = await self.get_submission(submission_id)
        if sub.user_id != user_id:
            raise AppError("PERMISSION_DENIED", "Not your submission", 403)
        if sub.status != SubmissionStatus.DRAFT:
            raise InvalidStateError("Only drafts can be deleted")
        await self.db.delete(sub)
        await self.db.flush()

    # ── Files ──

    async def upload_file(
        self,
        submission_id: str,
        deliverable_id: str,
        file_name: str,
        file_content: bytes,
        content_type: str,
        user_id: str,
    ) -> SubmissionItem:
        sub = await self.get_submission(submission_id)
        if sub.user_id != user_id:
            raise AppError("PERMISSION_DENIED", "Not your submission", 403)
        if sub.status != SubmissionStatus.DRAFT:
            raise InvalidStateError("Can only upload to drafts")

        if len(file_content) > MAX_FILE_SIZE:
            raise FileTooLargeError()

        # Clean filename
        safe_name = re.sub(r"[^\w.\-]", "_", file_name)
        file_key = (
            f"orgs/{sub.org_id}/submissions/{submission_id}/{deliverable_id}/{ULID()}_{safe_name}"
        )

        # Upload to S3
        from app.core.storage import get_s3_client

        async for client in get_s3_client():
            await client.put_object(
                Bucket=settings.s3_bucket,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
            )

        item = SubmissionItem(
            submission_id=submission_id,
            deliverable_id=deliverable_id,
            type=ItemType.FILE,
            file_key=file_key,
            file_name=file_name,
            file_size=len(file_content),
            mime_type=content_type,
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def get_download_url(self, file_id: str) -> str:
        item = await self.db.get(SubmissionItem, file_id)
        if item is None or not item.file_key:
            raise AppError("FILE_NOT_FOUND", "File not found", 404)

        from app.core.storage import get_s3_client

        async for client in get_s3_client():
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.s3_bucket, "Key": item.file_key},
                ExpiresIn=3600,
            )
            return url
        raise AppError("S3_ERROR", "Could not generate download URL", 500)  # pragma: no cover

    async def delete_file(self, file_id: str, user_id: str) -> None:
        item = await self.db.get(SubmissionItem, file_id)
        if item is None:
            raise AppError("FILE_NOT_FOUND", "File not found", 404)

        sub = await self.get_submission(item.submission_id)
        if sub.user_id != user_id:
            raise AppError("PERMISSION_DENIED", "Not your submission", 403)
        if sub.status != SubmissionStatus.DRAFT:
            raise InvalidStateError("Can only delete files from drafts")

        await self.db.delete(item)
        await self.db.flush()

    # ── Reviews ──

    async def create_review(
        self,
        submission_id: str,
        reviewer_id: str,
        status: str,
        score: int | None,
        score_breakdown: dict | None,
        feedback: str | None,
    ) -> SubmissionReview:
        sub = await self.get_submission(submission_id)
        project = await self.get_project(sub.project_id)

        review_status = ReviewStatus(status)

        review = SubmissionReview(
            submission_id=submission_id,
            reviewer_id=reviewer_id,
            reviewer_type=ReviewerType.INSTRUCTOR,
            status=review_status,
            score=score,
            score_breakdown=score_breakdown,
            feedback=feedback,
        )
        self.db.add(review)

        # Update submission status
        if review_status == ReviewStatus.APPROVED:
            sub.status = SubmissionStatus.APPROVED
            sub.final_score = self._calculate_final_score(score or 0, sub.is_late, project)
        elif review_status == ReviewStatus.REVISION_REQUESTED:
            sub.status = SubmissionStatus.REVISION_REQUESTED
        elif review_status == ReviewStatus.REJECTED:
            sub.status = SubmissionStatus.REJECTED
            sub.final_score = score

        await self.db.flush()

        log.info("submission_reviewed", submission_id=sub.id, status=status, score=sub.final_score)
        return review

    async def list_reviews(self, submission_id: str) -> list[SubmissionReview]:
        result = await self.db.execute(
            select(SubmissionReview)
            .where(SubmissionReview.submission_id == submission_id)
            .order_by(SubmissionReview.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_reviews(
        self,
        org_id: str,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Submission], int]:
        base = select(Submission).where(
            Submission.org_id == org_id,
            Submission.status == SubmissionStatus.SUBMITTED,
        )
        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()

        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(Submission.submitted_at).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    # ── Extensions ──

    async def grant_extension(
        self,
        project_id: str,
        user_id: str,
        new_deadline: datetime,
        reason: str | None,
        granted_by: str,
    ) -> SubmissionExtension:
        project = await self.get_project(project_id)

        ext = SubmissionExtension(
            project_id=project_id,
            user_id=user_id,
            original_deadline=project.deadline or datetime.now(UTC),
            extended_deadline=new_deadline,
            reason=reason,
            granted_by=granted_by,
        )
        self.db.add(ext)
        await self.db.flush()

        log.info(
            "extension_granted",
            project_id=project_id,
            user_id=user_id,
            deadline=new_deadline.isoformat(),
        )
        return ext

    # ── Timing ──

    async def get_submission_timing(self, project: Project, user_id: str) -> str:
        """Return 'on_time', 'late', or 'closed'."""
        effective = await self._get_effective_deadline(project, user_id)
        if effective is None:
            return "on_time"

        now = datetime.now(UTC)
        if now <= project.deadline if project.deadline else True:
            return "on_time"  # pragma: no cover

        # Check personal extension
        ext_result = await self.db.execute(
            select(SubmissionExtension).where(
                SubmissionExtension.project_id == project.id,
                SubmissionExtension.user_id == user_id,
            )
        )
        ext = ext_result.scalar_one_or_none()
        if ext and now <= ext.extended_deadline:
            return "on_time"

        if project.late_deadline and now <= project.late_deadline:
            return "late"

        return "closed"

    # ── Helpers ──

    async def _get_effective_deadline(self, project: Project, user_id: str) -> datetime | None:
        ext_result = await self.db.execute(
            select(SubmissionExtension).where(
                SubmissionExtension.project_id == project.id,
                SubmissionExtension.user_id == user_id,
            )
        )
        ext = ext_result.scalar_one_or_none()
        if ext:
            return ext.extended_deadline
        return project.late_deadline or project.deadline

    async def _validate_required_deliverables(self, submission: Submission) -> None:
        deliverables = await self.list_deliverables(submission.project_id)
        required_ids = {d.id for d in deliverables if d.required}

        if not required_ids:
            return

        result = await self.db.execute(
            select(SubmissionItem.deliverable_id)
            .where(SubmissionItem.submission_id == submission.id)
            .distinct()
        )
        submitted_ids = set(result.scalars().all())

        missing = required_ids - submitted_ids
        if missing:
            raise MissingDeliverablesError()

    async def _count_user_submissions(self, project_id: str, user_id: str) -> int:
        result = await self.db.execute(
            select(func.count(Submission.id)).where(
                Submission.project_id == project_id,
                Submission.user_id == user_id,
            )
        )
        return result.scalar_one()

    async def _set_project_skills(self, project_id: str, skill_ids: list[str]) -> None:
        existing = await self.db.execute(
            select(ProjectSkill).where(ProjectSkill.project_id == project_id)
        )
        for ps in existing.scalars():
            await self.db.delete(ps)
        for sid in skill_ids:
            self.db.add(ProjectSkill(project_id=project_id, skill_id=sid))
        await self.db.flush()

    @staticmethod
    def _calculate_final_score(score: int, is_late: bool, project: Project) -> int:
        if is_late and project.late_penalty_pct > 0:
            penalty = score * project.late_penalty_pct / 100
            return max(0, round(score - penalty))
        return score

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:200]
