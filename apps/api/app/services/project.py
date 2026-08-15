"""Project, submission, review, and file upload service."""

import json
import re
import secrets
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.config import settings
from app.core.media import (
    AUDIO_MIMES,
    IMAGE_MIMES,
    MEDIA_ALL,
    VIDEO_MIMES,
    content_matches_mime,
)
from app.exceptions import AppError
from app.models.project import (
    CommentAnchorType,
    DeliverableType,
    ItemType,
    Project,
    ProjectAsset,
    ProjectDeliverable,
    ProjectSkill,
    ProjectTemplate,
    ReviewerType,
    ReviewStatus,
    Submission,
    SubmissionComment,
    SubmissionExtension,
    SubmissionItem,
    SubmissionReview,
    SubmissionStatus,
)
from app.models.skill import ContentStatus, DifficultyLevel

log = structlog.get_logger()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

PROJECT_TYPES = {"general", "ai_visual"}

# Per-deliverable-type MIME whitelist. FILE stays unrestricted (back-compat).
MEDIA_MIME_WHITELIST: dict[DeliverableType, set[str]] = {
    DeliverableType.IMAGE: IMAGE_MIMES,
    DeliverableType.VIDEO: VIDEO_MIMES,
    DeliverableType.AUDIO: AUDIO_MIMES,
    DeliverableType.REFERENCE: MEDIA_ALL,
    DeliverableType.FINAL_OUTPUT: MEDIA_ALL,
}


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
    def __init__(self, limit_mb: int = MAX_FILE_SIZE // (1024 * 1024)):
        super().__init__(
            "FILE_TOO_LARGE",
            f"File exceeds maximum size of {limit_mb}MB",
            413,
        )


class UnsupportedMediaTypeError(AppError):
    def __init__(self, mime: str):
        super().__init__(
            "UNSUPPORTED_MEDIA_TYPE",
            f"Content type '{mime}' is not accepted for this deliverable",
            422,
        )


class ContentTypeMismatchError(AppError):
    def __init__(self):
        super().__init__(
            "CONTENT_TYPE_MISMATCH",
            "File content does not match the declared content type",
            422,
        )


class MaxFilesReachedError(AppError):
    def __init__(self, limit: int):
        super().__init__(
            "MAX_FILES_REACHED",
            f"Maximum of {limit} files reached for this deliverable",
            422,
        )


class TemplateNotFoundError(AppError):
    def __init__(self):
        super().__init__("TEMPLATE_NOT_FOUND", "Project template not found", 404)


class AssetNotFoundError(AppError):
    def __init__(self):
        super().__init__("ASSET_NOT_FOUND", "Project asset not found", 404)


# ── Builtin templates ─────────────────────────────────────────
# Defined in code (not DB) so they ship with the app, need no seeding,
# and are available to every organization out of the box.

BUILTIN_TEMPLATES: list[dict] = [
    {
        "id": "builtin-ai-product-ad",
        "name": "AI Product Advertisement",
        "description": (
            "Produce a complete AI-generated product advertisement: from client "
            "brief through concept, prompt design, key visuals, and storyboard "
            "to the final video deliverable."
        ),
        "instructions": (
            "# AI Product Advertisement\n\n"
            "Work through the production pipeline stage by stage. Each stage has "
            "a deliverable — complete them in order.\n\n"
            "1. **Client Brief** — summarize the client's product, audience, and goals.\n"
            "2. **Creative Concept** — describe your creative direction in markdown.\n"
            "3. **Reference Assets** — collect style/brand references.\n"
            "4. **Prompt Design** — craft and document your generation prompts.\n"
            "5. **Key Visuals** — generate and upload the hero images.\n"
            "6. **Storyboard** — assemble the shot sequence as images.\n"
            "7. **Video Clips** — generate the individual video segments.\n"
            "8. **Final Video** — deliver the finished advertisement."
        ),
        "project_type": "ai_visual",
        "difficulty": "intermediate",
        "suggested_minutes": 480,
        "max_score": 100,
        "rubric": [
            {"criterion": "Concept & Brief Alignment", "max_score": 20},
            {"criterion": "Prompt Craftsmanship", "max_score": 20},
            {"criterion": "Visual Quality", "max_score": 25},
            {"criterion": "Storytelling & Storyboard", "max_score": 15},
            {"criterion": "Final Video Production", "max_score": 20},
        ],
        "deliverables": [
            {
                "name": "Client Brief",
                "description": "Summary of the product, target audience, and campaign goals.",
                "type": "text",
                "required": True,
                "config": {},
                "sort_order": 0,
            },
            {
                "name": "Creative Concept",
                "description": "Creative direction, mood, and visual language (markdown).",
                "type": "markdown",
                "required": True,
                "config": {},
                "sort_order": 1,
            },
            {
                "name": "Reference Assets",
                "description": "Style, brand, or product references you are working from.",
                "type": "reference",
                "required": False,
                "config": {"max_files": 10, "max_file_size_mb": 25},
                "sort_order": 2,
            },
            {
                "name": "Prompt Design",
                "description": "The generation prompt(s) with tool, model, and parameters.",
                "type": "prompt",
                "required": True,
                "config": {},
                "sort_order": 3,
            },
            {
                "name": "Key Visuals",
                "description": "Hero images for the advertisement.",
                "type": "image",
                "required": True,
                "config": {
                    "accepted_formats": ["image/png", "image/jpeg", "image/webp"],
                    "max_files": 5,
                    "max_file_size_mb": 25,
                },
                "sort_order": 4,
            },
            {
                "name": "Storyboard",
                "description": "Ordered shot sequence as images.",
                "type": "image",
                "required": True,
                "config": {
                    "accepted_formats": ["image/png", "image/jpeg", "image/webp"],
                    "max_files": 12,
                    "max_file_size_mb": 25,
                },
                "sort_order": 5,
            },
            {
                "name": "Video Clips",
                "description": "Individual generated video segments.",
                "type": "video",
                "required": False,
                "config": {"max_files": 8, "max_file_size_mb": 50},
                "sort_order": 6,
            },
            {
                "name": "Final Video",
                "description": "The finished advertisement video.",
                "type": "final_output",
                "required": True,
                "config": {
                    "accepted_formats": ["video/mp4", "video/webm"],
                    "max_files": 1,
                    "max_file_size_mb": 50,
                },
                "sort_order": 7,
            },
        ],
        "skill_names": ["Prompt Engineering", "AI Image Generation", "AI Video Production"],
    },
]


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
        project_type: str = "general",
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
            project_type=project_type if project_type in PROJECT_TYPES else "general",
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
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            project.slug = f"{project.slug}-{secrets.token_hex(3)}"
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
        # Validate the ordering on the COMBINED (post-update) values — a partial
        # update that changes only one of deadline/late_deadline can otherwise
        # leave a late_deadline earlier than the deadline (negative late window).
        if (
            project.deadline is not None
            and project.late_deadline is not None
            and project.late_deadline < project.deadline
        ):
            raise InvalidStateError("late_deadline must be on or after deadline")
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
    ) -> tuple[list[tuple[Submission, str]], int]:
        """List submissions with author display names as (submission, name) tuples."""
        from app.models.user import User as UserModel

        base = select(Submission).where(Submission.project_id == project_id)
        if user_id:
            base = base.where(Submission.user_id == user_id)

        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()

        offset = (page - 1) * per_page
        joined = (
            select(Submission, UserModel.display_name)
            .join(UserModel, UserModel.id == Submission.user_id)
            .where(Submission.project_id == project_id)
        )
        if user_id:
            joined = joined.where(Submission.user_id == user_id)
        result = await self.db.execute(
            joined.order_by(Submission.created_at.desc()).offset(offset).limit(per_page)
        )
        return [(sub, name) for sub, name in result.all()], total

    async def submit_draft(self, submission_id: str, user_id: str) -> Submission:
        sub = await self.get_submission(submission_id)

        if sub.user_id != user_id:
            raise AppError("PERMISSION_DENIED", "Not your submission", 403)
        # A draft OR a revision-requested submission can be (re)submitted.
        if sub.status not in (SubmissionStatus.DRAFT, SubmissionStatus.REVISION_REQUESTED):
            raise InvalidStateError("Only drafts or revision-requested submissions can be submitted")

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

    def _validate_media_upload(
        self,
        deliverable: ProjectDeliverable,
        file_content: bytes,
        content_type: str,
    ) -> None:
        """MIME whitelist + magic-byte + per-deliverable config enforcement."""
        whitelist = MEDIA_MIME_WHITELIST.get(deliverable.type)
        config = deliverable.config or {}

        if whitelist is not None:
            allowed = whitelist
            # Instructor-configured accepted_formats can only NARROW the safe set
            accepted = config.get("accepted_formats")
            if isinstance(accepted, list) and accepted:
                narrowed = {m.lower() for m in accepted if isinstance(m, str)} & whitelist
                if narrowed:
                    allowed = narrowed
            if content_type.lower() not in allowed:
                raise UnsupportedMediaTypeError(content_type)
            # Never trust the declared type: sniff actual file signature
            if not content_matches_mime(file_content[:16], content_type):
                raise ContentTypeMismatchError()

        # Per-deliverable size limit — can only tighten, never exceed global cap
        max_mb = config.get("max_file_size_mb")
        if isinstance(max_mb, (int, float)) and max_mb > 0:
            limit = min(int(max_mb) * 1024 * 1024, MAX_FILE_SIZE)
            if len(file_content) > limit:
                raise FileTooLargeError(limit // (1024 * 1024))

    async def _next_item_version(self, submission_id: str, deliverable_id: str) -> int:
        result = await self.db.execute(
            select(func.count(SubmissionItem.id)).where(
                SubmissionItem.submission_id == submission_id,
                SubmissionItem.deliverable_id == deliverable_id,
            )
        )
        return result.scalar_one() + 1

    async def upload_file(
        self,
        submission_id: str,
        deliverable_id: str,
        file_name: str,
        file_content: bytes,
        content_type: str,
        user_id: str,
        note: str | None = None,
    ) -> SubmissionItem:
        sub = await self.get_submission(submission_id)
        if sub.user_id != user_id:
            raise AppError("PERMISSION_DENIED", "Not your submission", 403)
        if sub.status not in (SubmissionStatus.DRAFT, SubmissionStatus.REVISION_REQUESTED):
            raise InvalidStateError("Can only upload while the submission is editable")

        # Deliverable must exist and belong to this submission's project
        deliverable = await self.get_deliverable(deliverable_id)
        if deliverable.project_id != sub.project_id:
            raise DeliverableNotFoundError()

        if len(file_content) > MAX_FILE_SIZE:
            raise FileTooLargeError()

        self._validate_media_upload(deliverable, file_content, content_type)

        # max_files caps total stored items for this deliverable. Single-slot
        # deliverables (max_files=1) are exempt so "replace with new version"
        # keeps working; multi-slot ones can free space via delete_file.
        config = deliverable.config or {}
        max_files = config.get("max_files")
        version = await self._next_item_version(submission_id, deliverable_id)
        if isinstance(max_files, int) and max_files > 1 and version > max_files:
            raise MaxFilesReachedError(max_files)

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

        # Auto-extract generation metadata from AI-tool PNGs (A1111/ComfyUI).
        # Stored as JSON in the item's content column (NULL otherwise).
        gen_content = None
        if deliverable.type in (
            DeliverableType.IMAGE,
            DeliverableType.REFERENCE,
            DeliverableType.FINAL_OUTPUT,
        ):
            from app.core.genmeta import extract_generation_metadata

            gen_meta = extract_generation_metadata(file_content, content_type)
            if gen_meta:
                gen_content = json.dumps({"generation": gen_meta}, ensure_ascii=False)

        item = SubmissionItem(
            submission_id=submission_id,
            deliverable_id=deliverable_id,
            type=ItemType.FILE,
            content=gen_content,
            file_key=file_key,
            file_name=file_name,
            file_size=len(file_content),
            mime_type=content_type,
            version=version,
            note=note,
            uploaded_by=user_id,
        )
        self.db.add(item)
        await self.db.flush()
        log.info(
            "file_uploaded",
            submission_id=submission_id,
            deliverable_id=deliverable_id,
            version=version,
            size=len(file_content),
            has_gen_meta=gen_content is not None,
        )
        return item

    async def get_download_url(self, file_id: str, submission_id: str | None = None) -> str:
        item = await self.db.get(SubmissionItem, file_id)
        if item is None or not item.file_key:
            raise AppError("FILE_NOT_FOUND", "File not found", 404)
        # The file must belong to the submission the caller was authorized for —
        # otherwise a user can pass their own submission path + another user's
        # file_id and receive a presigned URL for a file they can't access (IDOR).
        if submission_id is not None and item.submission_id != submission_id:
            raise AppError("FILE_NOT_FOUND", "File not found", 404)

        from app.core.storage import get_s3_client

        params: dict = {"Bucket": settings.s3_bucket, "Key": item.file_key}
        # Pin content type from DB (never trust stored object metadata) and
        # force inline disposition so media previews render in-browser.
        if item.mime_type:
            params["ResponseContentType"] = item.mime_type
            params["ResponseContentDisposition"] = "inline"

        async for client in get_s3_client():
            url = await client.generate_presigned_url(
                "get_object",
                Params=params,
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
        if sub.status not in (SubmissionStatus.DRAFT, SubmissionStatus.REVISION_REQUESTED):
            raise InvalidStateError("Can only delete files while the submission is editable")

        # Best-effort S3 cleanup — don't leave orphaned objects behind
        if item.file_key:
            from app.core.storage import get_s3_client

            try:
                async for client in get_s3_client():
                    await client.delete_object(Bucket=settings.s3_bucket, Key=item.file_key)
            except Exception:  # noqa: BLE001
                log.warning("file_s3_delete_failed", file_id=file_id, key=item.file_key)

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

        # Only submitted work can be reviewed — a draft hasn't been handed in
        if sub.status in (SubmissionStatus.DRAFT,):
            raise InvalidStateError("Cannot review a draft submission")

        # Score cannot exceed this project's configured maximum
        if score is not None and score > project.max_score:
            raise AppError(
                "SCORE_EXCEEDS_MAX",
                f"Score {score} exceeds project maximum of {project.max_score}",
                422,
            )

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
    ) -> tuple[list[tuple[Submission, str, str, str]], int]:
        """Pending submissions enriched with author display name and project title.

        Returns (submission, author_name, project_title, project_id) tuples so
        the review dashboard can show WHO submitted WHAT — not bare ULIDs.
        """
        from app.models.user import User as UserModel

        base = select(Submission).where(
            Submission.org_id == org_id,
            Submission.status == SubmissionStatus.SUBMITTED,
        )
        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()

        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Submission, UserModel.display_name, Project.title)
            .join(UserModel, UserModel.id == Submission.user_id)
            .join(Project, Project.id == Submission.project_id)
            .where(
                Submission.org_id == org_id,
                Submission.status == SubmissionStatus.SUBMITTED,
            )
            .order_by(Submission.submitted_at)
            .offset(offset)
            .limit(per_page)
        )
        rows = [(sub, name, title, sub.project_id) for sub, name, title in result.all()]
        return rows, total

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

        # The recipient must be an active member of the project's org — otherwise
        # a bogus id 500s on the FK and a real outsider gets a phantom extension.
        from app.models.organization import MemberStatus, OrgMember

        member = await self.db.execute(
            select(OrgMember.id).where(
                OrgMember.org_id == project.org_id,
                OrgMember.user_id == user_id,
                OrgMember.status == MemberStatus.ACTIVE,
            )
        )
        if member.scalar_one_or_none() is None:
            raise AppError("USER_NOT_FOUND", "User is not a member of this organization", 404)

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
        if project.deadline is None:
            return "on_time"  # No deadline set

        now = datetime.now(UTC)

        # Check personal extension first
        ext_result = await self.db.execute(
            select(SubmissionExtension).where(
                SubmissionExtension.project_id == project.id,
                SubmissionExtension.user_id == user_id,
            )
        )
        ext = ext_result.scalar_one_or_none()

        # On time: before deadline or before personal extension
        if now <= project.deadline:
            return "on_time"
        if ext and now <= ext.extended_deadline:
            return "on_time"

        # Late: between deadline and late_deadline
        if project.late_deadline and now <= project.late_deadline:
            return "late"

        # Closed: past all deadlines
        return "closed"

    # ── Helpers ──

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
        # Every skill must exist AND belong to the project's org (bogus IDs
        # 500 on the FK; cross-org links would leak another org's skills).
        if skill_ids:
            from app.models.skill import Skill

            project = await self.get_project(project_id)
            found = await self.db.execute(
                select(Skill.id).where(Skill.id.in_(skill_ids), Skill.org_id == project.org_id)
            )
            valid = set(found.scalars())
            if set(skill_ids) - valid:
                raise AppError("SKILL_NOT_FOUND", "Skill not found in this organization", 404)

        existing = await self.db.execute(
            select(ProjectSkill).where(ProjectSkill.project_id == project_id)
        )
        for ps in existing.scalars():
            await self.db.delete(ps)
        await self.db.flush()
        # De-dup: a repeated skill_id would violate the composite PK with a 500.
        for sid in dict.fromkeys(skill_ids):
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

    # ── Project Templates ─────────────────────────────────────

    async def create_template(
        self,
        org_id: str,
        created_by: str,
        *,
        name: str,
        description: str,
        instructions: str,
        project_type: str = "general",
        difficulty: str = "intermediate",
        suggested_minutes: int | None = None,
        max_score: int = 100,
        rubric: list[dict],
        deliverables: list[dict],
        skill_names: list[str] | None = None,
    ) -> ProjectTemplate:
        try:
            diff = DifficultyLevel(difficulty)
        except ValueError:
            diff = DifficultyLevel.INTERMEDIATE

        template = ProjectTemplate(
            org_id=org_id,
            name=name,
            description=description,
            instructions=instructions,
            project_type=project_type if project_type in PROJECT_TYPES else "general",
            difficulty=diff,
            suggested_minutes=suggested_minutes,
            max_score=max_score,
            rubric=rubric,
            deliverables=deliverables,
            skill_names=skill_names or [],
            created_by=created_by,
        )
        self.db.add(template)
        await self.db.flush()
        log.info("template_created", template_id=template.id, org_id=org_id)
        return template

    async def list_templates(self, org_id: str) -> tuple[list[dict], list[ProjectTemplate]]:
        """Return (builtin template dicts, org-created templates)."""
        result = await self.db.execute(
            select(ProjectTemplate)
            .where(
                ProjectTemplate.org_id == org_id,
                ProjectTemplate.status != ContentStatus.ARCHIVED,
            )
            .order_by(ProjectTemplate.created_at.desc())
        )
        return list(BUILTIN_TEMPLATES), list(result.scalars().all())

    async def get_template(self, template_id: str, org_id: str) -> ProjectTemplate | dict:
        """Builtin templates are addressable by their 'builtin-' id."""
        if template_id.startswith("builtin-"):
            for t in BUILTIN_TEMPLATES:
                if t["id"] == template_id:
                    return t
            raise TemplateNotFoundError()

        template = await self.db.get(ProjectTemplate, template_id)
        if (
            template is None
            or template.org_id != org_id
            or template.status == ContentStatus.ARCHIVED
        ):
            raise TemplateNotFoundError()
        return template

    async def update_template(self, template_id: str, org_id: str, **fields) -> ProjectTemplate:
        template = await self.get_template(template_id, org_id)
        if isinstance(template, dict):
            raise AppError("BUILTIN_READONLY", "Built-in templates cannot be modified", 422)
        for k, v in fields.items():
            if v is not None and hasattr(template, k):
                if k == "difficulty":
                    v = DifficultyLevel(v)
                setattr(template, k, v)
        await self.db.flush()
        return template

    async def delete_template(self, template_id: str, org_id: str) -> None:
        template = await self.get_template(template_id, org_id)
        if isinstance(template, dict):
            raise AppError("BUILTIN_READONLY", "Built-in templates cannot be deleted", 422)
        template.status = ContentStatus.ARCHIVED
        await self.db.flush()

    async def create_project_from_template(
        self,
        org_id: str,
        template_id: str,
        created_by: str,
        title: str | None = None,
    ) -> Project:
        """Instantiate a project from a template.

        Deliverables are deep-copied into real ProjectDeliverable rows, so the
        resulting project and the template are fully independent.
        """
        template = await self.get_template(template_id, org_id)

        if isinstance(template, dict):
            src = template
        else:
            src = {
                "name": template.name,
                "description": template.description,
                "instructions": template.instructions,
                "project_type": template.project_type,
                "difficulty": template.difficulty.value,
                "max_score": template.max_score,
                "rubric": template.rubric,
                "deliverables": template.deliverables,
            }

        project = await self.create_project(
            org_id=org_id,
            title=title or src["name"],
            slug=None,
            description=src["description"],
            instructions=src["instructions"],
            difficulty=src["difficulty"],
            max_score=src["max_score"],
            rubric=[dict(r) for r in src["rubric"]],
            deadline=None,
            late_deadline=None,
            late_penalty_pct=0,
            max_submissions=0,
            skill_ids=None,
            created_by=created_by,
            project_type=src.get("project_type", "general"),
        )

        for d in src.get("deliverables", []):
            await self.create_deliverable(
                project.id,
                d["name"],
                d.get("description"),
                d["type"],
                d.get("required", True),
                dict(d.get("config") or {}),
                d.get("sort_order", 0),
            )

        await self.db.flush()
        log.info(
            "project_created_from_template",
            project_id=project.id,
            template_id=template_id,
            org_id=org_id,
        )
        return project

    # ── Project Assets (instructor reference material) ────────

    async def upload_asset(
        self,
        org_id: str,
        project_id: str,
        name: str,
        description: str | None,
        file_name: str,
        file_content: bytes,
        content_type: str,
        uploaded_by: str,
    ) -> ProjectAsset:
        await self.get_project(project_id)

        if len(file_content) > MAX_FILE_SIZE:
            raise FileTooLargeError()

        # Assets must be previewable media or PDF — sniff to block spoofing
        if content_type.lower() not in MEDIA_ALL:
            raise UnsupportedMediaTypeError(content_type)
        if not content_matches_mime(file_content[:16], content_type):
            raise ContentTypeMismatchError()

        safe_name = re.sub(r"[^\w.\-]", "_", file_name)
        file_key = f"orgs/{org_id}/projects/{project_id}/assets/{ULID()}_{safe_name}"

        from app.core.storage import get_s3_client

        async for client in get_s3_client():
            await client.put_object(
                Bucket=settings.s3_bucket,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
            )

        asset = ProjectAsset(
            org_id=org_id,
            project_id=project_id,
            name=name,
            description=description,
            file_key=file_key,
            file_name=file_name,
            file_size=len(file_content),
            mime_type=content_type,
            uploaded_by=uploaded_by,
        )
        self.db.add(asset)
        await self.db.flush()
        log.info("asset_uploaded", asset_id=asset.id, project_id=project_id)
        return asset

    async def list_assets(self, project_id: str) -> list[ProjectAsset]:
        result = await self.db.execute(
            select(ProjectAsset)
            .where(ProjectAsset.project_id == project_id)
            .order_by(ProjectAsset.sort_order, ProjectAsset.created_at)
        )
        return list(result.scalars().all())

    async def get_asset(self, asset_id: str, org_id: str) -> ProjectAsset:
        asset = await self.db.get(ProjectAsset, asset_id)
        if asset is None or asset.org_id != org_id:
            raise AssetNotFoundError()
        return asset

    async def get_asset_download_url(self, asset_id: str, org_id: str) -> str:
        asset = await self.get_asset(asset_id, org_id)

        from app.core.storage import get_s3_client

        async for client in get_s3_client():
            url = await client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.s3_bucket,
                    "Key": asset.file_key,
                    "ResponseContentType": asset.mime_type,
                    "ResponseContentDisposition": "inline",
                },
                ExpiresIn=3600,
            )
            return url
        raise AppError("S3_ERROR", "Could not generate download URL", 500)  # pragma: no cover

    async def delete_asset(self, asset_id: str, org_id: str) -> None:
        asset = await self.get_asset(asset_id, org_id)

        from app.core.storage import get_s3_client

        try:
            async for client in get_s3_client():
                await client.delete_object(Bucket=settings.s3_bucket, Key=asset.file_key)
        except Exception:  # noqa: BLE001 — best-effort cleanup
            log.warning("asset_s3_delete_failed", asset_id=asset_id, key=asset.file_key)

        await self.db.delete(asset)
        await self.db.flush()

    # ── Prompt items ──────────────────────────────────────────

    async def add_prompt_item(
        self,
        submission_id: str,
        deliverable_id: str,
        prompt_data: dict,
        user_id: str,
    ) -> SubmissionItem:
        sub = await self.get_submission(submission_id)
        if sub.user_id != user_id:
            raise AppError("PERMISSION_DENIED", "Not your submission", 403)
        if sub.status not in (SubmissionStatus.DRAFT, SubmissionStatus.REVISION_REQUESTED):
            raise InvalidStateError("Can only add prompts while the submission is editable")

        deliverable = await self.get_deliverable(deliverable_id)
        if deliverable.project_id != sub.project_id:
            raise DeliverableNotFoundError()
        if deliverable.type != DeliverableType.PROMPT:
            raise AppError("INVALID_TYPE", "Deliverable is not a prompt deliverable", 422)

        version = await self._next_item_version(submission_id, deliverable_id)

        item = SubmissionItem(
            submission_id=submission_id,
            deliverable_id=deliverable_id,
            type=ItemType.PROMPT,
            content=json.dumps(prompt_data, ensure_ascii=False),
            version=version,
            uploaded_by=user_id,
        )
        self.db.add(item)
        await self.db.flush()
        log.info(
            "prompt_item_added",
            submission_id=submission_id,
            deliverable_id=deliverable_id,
            version=version,
        )
        return item

    # ── Anchored comments ─────────────────────────────────────

    async def add_comment(
        self,
        org_id: str,
        submission_id: str,
        item_id: str,
        author_id: str,
        *,
        text: str,
        anchor_type: str = "global",
        timestamp_ms: int | None = None,
        duration_ms: int | None = None,
        region: dict | None = None,
        parent_id: str | None = None,
    ) -> SubmissionComment:
        await self.get_submission(submission_id)  # 404 if missing

        # Item must belong to this submission
        item = await self.db.get(SubmissionItem, item_id)
        if item is None or item.submission_id != submission_id:
            raise AppError("ITEM_NOT_FOUND", "Submission item not found", 404)

        try:
            anchor = CommentAnchorType(anchor_type)
        except ValueError as exc:
            raise AppError("INVALID_ANCHOR", f"Invalid anchor type: {anchor_type}", 422) from exc

        # Anchor consistency
        if anchor == CommentAnchorType.TIME and timestamp_ms is None:
            raise AppError("INVALID_ANCHOR", "Time anchor requires timestamp_ms", 422)
        if anchor == CommentAnchorType.REGION and not region:
            raise AppError("INVALID_ANCHOR", "Region anchor requires region geometry", 422)
        if anchor != CommentAnchorType.TIME:
            timestamp_ms = None
            duration_ms = None
        if anchor != CommentAnchorType.REGION:
            region = None

        # Replies inherit the thread; must reference a comment on the same item
        if parent_id:
            parent = await self.db.get(SubmissionComment, parent_id)
            if parent is None or parent.item_id != item_id:
                raise AppError("COMMENT_NOT_FOUND", "Parent comment not found", 404)
            if parent.parent_id is not None:
                # Keep threads one level deep (Frame.io model)
                parent_id = parent.parent_id

        comment = SubmissionComment(
            org_id=org_id,
            submission_id=submission_id,
            item_id=item_id,
            author_id=author_id,
            parent_id=parent_id,
            text=text,
            anchor_type=anchor,
            timestamp_ms=timestamp_ms,
            duration_ms=duration_ms,
            region=region,
        )
        self.db.add(comment)
        await self.db.flush()
        log.info("comment_added", submission_id=submission_id, item_id=item_id, anchor=anchor.value)
        return comment

    async def list_comments(self, submission_id: str) -> list[SubmissionComment]:
        result = await self.db.execute(
            select(SubmissionComment)
            .where(SubmissionComment.submission_id == submission_id)
            .order_by(SubmissionComment.created_at)
        )
        return list(result.scalars().all())

    async def get_comment(self, comment_id: str, org_id: str) -> SubmissionComment:
        comment = await self.db.get(SubmissionComment, comment_id)
        if comment is None or comment.org_id != org_id:
            raise AppError("COMMENT_NOT_FOUND", "Comment not found", 404)
        return comment

    async def set_comment_completed(
        self, comment_id: str, org_id: str, completed: bool
    ) -> SubmissionComment:
        comment = await self.get_comment(comment_id, org_id)
        comment.completed = completed
        await self.db.flush()
        return comment

    async def delete_comment(self, comment_id: str, org_id: str, user_id: str) -> None:
        comment = await self.get_comment(comment_id, org_id)
        if comment.author_id != user_id:
            raise AppError("PERMISSION_DENIED", "Only the author can delete a comment", 403)
        await self.db.delete(comment)
        await self.db.flush()
