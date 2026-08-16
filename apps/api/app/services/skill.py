"""Skill, exercise, attempt, and progress service."""

import re
import secrets
from collections import deque
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.skill import (
    ContentStatus,
    DifficultyLevel,
    Exercise,
    ExerciseAttempt,
    ExerciseType,
    GradingMethod,
    ProgressStatus,
    Skill,
    SkillCategory,
    SkillPrerequisite,
    SkillProgress,
)

log = structlog.get_logger()


# ── Errors ────────────────────────────────────────────────────


class CategoryNotFoundError(AppError):
    def __init__(self):
        super().__init__("CATEGORY_NOT_FOUND", "Skill category not found", 404)


class SkillNotFoundError(AppError):
    def __init__(self):
        super().__init__("SKILL_NOT_FOUND", "Skill not found", 404)


class ExerciseNotFoundError(AppError):
    def __init__(self):
        super().__init__("EXERCISE_NOT_FOUND", "Exercise not found", 404)


class AttemptNotFoundError(AppError):
    def __init__(self):
        super().__init__("ATTEMPT_NOT_FOUND", "Attempt not found", 404)


class SkillLockedError(AppError):
    def __init__(self):
        super().__init__("SKILL_LOCKED", "Prerequisite skills not completed", 403)


class CyclicDependencyError(AppError):
    def __init__(self):
        super().__init__("CYCLIC_DEPENDENCY", "Circular prerequisite dependency detected", 422)


# ── Service ───────────────────────────────────────────────────


class SkillService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Categories ──

    async def create_category(
        self,
        org_id: str,
        name: str,
        slug: str | None,
        description: str | None,
        icon: str | None,
        created_by: str,
    ) -> SkillCategory:
        if slug is None:
            slug = self._generate_slug(name)
        cat = SkillCategory(
            org_id=org_id,
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            status=ContentStatus.PUBLISHED,
            created_by=created_by,
        )
        self.db.add(cat)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            cat.slug = f"{cat.slug}-{secrets.token_hex(3)}"
            self.db.add(cat)
            await self.db.flush()
        return cat

    async def list_categories(self, org_id: str) -> list[SkillCategory]:
        result = await self.db.execute(
            select(SkillCategory)
            .where(SkillCategory.org_id == org_id, SkillCategory.status != ContentStatus.ARCHIVED)
            .order_by(SkillCategory.sort_order, SkillCategory.name)
        )
        return list(result.scalars().all())

    async def get_category(self, category_id: str) -> SkillCategory:
        cat = await self.db.get(SkillCategory, category_id)
        if cat is None or cat.status == ContentStatus.ARCHIVED:
            raise CategoryNotFoundError()
        return cat

    async def update_category(self, category_id: str, **fields) -> SkillCategory:
        cat = await self.get_category(category_id)
        for k, v in fields.items():
            if v is not None and hasattr(cat, k):
                setattr(cat, k, v)
        await self.db.flush()
        return cat

    async def delete_category(self, category_id: str) -> None:
        cat = await self.get_category(category_id)
        cat.status = ContentStatus.ARCHIVED
        await self.db.flush()

    # ── Skills ──

    async def create_skill(
        self,
        org_id: str,
        category_id: str,
        name: str,
        slug: str | None,
        description: str,
        learning_content: str | None,
        difficulty: str,
        estimated_minutes: int | None,
        tags: list[str] | None,
        prerequisite_ids: list[str] | None,
        created_by: str,
    ) -> Skill:
        if slug is None:
            slug = self._generate_slug(name)

        # Category must exist and belong to this org — otherwise the FK
        # violation is misread as a slug collision below and 500s on retry.
        await self._require_org_category(org_id, category_id)

        try:
            diff = DifficultyLevel(difficulty)
        except ValueError:
            diff = DifficultyLevel.BEGINNER

        skill = Skill(
            org_id=org_id,
            category_id=category_id,
            name=name,
            slug=slug,
            description=description,
            learning_content=learning_content,
            difficulty=diff,
            estimated_minutes=estimated_minutes,
            tags=tags or [],
            created_by=created_by,
        )
        self.db.add(skill)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            # Slug collision — append random suffix and retry
            skill.slug = f"{skill.slug}-{secrets.token_hex(3)}"
            self.db.add(skill)
            await self.db.flush()

        if prerequisite_ids:
            await self._set_prerequisites(skill.id, prerequisite_ids)

        log.info("skill_created", skill_id=skill.id, org_id=org_id)
        return skill

    async def list_skills(
        self,
        org_id: str,
        category_id: str | None = None,
        difficulty: str | None = None,
        status: str | None = None,
        tag: str | None = None,
        q: str | None = None,
        page: int = 1,
        per_page: int = 20,
        *,
        published_only: bool = False,
    ) -> tuple[list[Skill], int]:
        base = select(Skill).where(Skill.org_id == org_id)

        if category_id:
            base = base.where(Skill.category_id == category_id)
        if difficulty:
            # Bad query-string values must not 500 on the enum coercion.
            try:
                base = base.where(Skill.difficulty == DifficultyLevel(difficulty))
            except ValueError as exc:
                raise AppError("INVALID_FILTER", f"Invalid difficulty: {difficulty}", 422) from exc
        if published_only:
            # Students only see published skills — a draft skill an instructor
            # is still authoring must not appear in listings.
            base = base.where(Skill.status == ContentStatus.PUBLISHED)
        elif status:
            try:
                base = base.where(Skill.status == ContentStatus(status))
            except ValueError as exc:
                raise AppError("INVALID_FILTER", f"Invalid status: {status}", 422) from exc
        else:
            # By default, exclude archived skills
            base = base.where(Skill.status != ContentStatus.ARCHIVED)
        if tag:
            base = base.where(Skill.tags.contains([tag]))
        if q:
            base = base.where(Skill.name.ilike(f"%{q}%"))

        total_result = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_result.scalar_one()

        offset = (page - 1) * per_page
        result = await self.db.execute(
            base.order_by(Skill.sort_order, Skill.name).offset(offset).limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_skill(self, skill_id: str) -> Skill:
        skill = await self.db.get(Skill, skill_id)
        if skill is None or skill.status == ContentStatus.ARCHIVED:
            raise SkillNotFoundError()
        return skill

    async def get_skill_prerequisites(self, skill_id: str) -> list[Skill]:
        result = await self.db.execute(
            select(Skill)
            .join(SkillPrerequisite, SkillPrerequisite.prerequisite_id == Skill.id)
            .where(SkillPrerequisite.skill_id == skill_id)
        )
        return list(result.scalars().all())

    async def update_skill(self, skill_id: str, **fields) -> Skill:
        skill = await self.get_skill(skill_id)
        if fields.get("category_id") is not None:
            await self._require_org_category(skill.org_id, fields["category_id"])
        for k, v in fields.items():
            if v is not None and hasattr(skill, k):
                if k == "difficulty":
                    v = DifficultyLevel(v)
                setattr(skill, k, v)
        await self.db.flush()
        return skill

    async def _require_org_category(self, org_id: str, category_id: str) -> SkillCategory:
        cat = await self.db.get(SkillCategory, category_id)
        if cat is None or cat.org_id != org_id or cat.status == ContentStatus.ARCHIVED:
            raise AppError("CATEGORY_NOT_FOUND", "Category not found", 404)
        return cat

    async def delete_skill(self, skill_id: str) -> None:
        skill = await self.get_skill(skill_id)
        skill.status = ContentStatus.ARCHIVED
        await self.db.flush()

    async def publish_skill(self, skill_id: str) -> Skill:
        skill = await self.get_skill(skill_id)
        skill.status = ContentStatus.PUBLISHED
        skill.published_at = datetime.now(UTC)
        await self.db.flush()
        return skill

    async def unpublish_skill(self, skill_id: str) -> Skill:
        skill = await self.get_skill(skill_id)
        skill.status = ContentStatus.DRAFT
        await self.db.flush()
        return skill

    async def set_prerequisites(self, skill_id: str, prerequisite_ids: list[str]) -> None:
        await self._set_prerequisites(skill_id, prerequisite_ids)
        await self.db.flush()

    # ── Exercises ──

    async def create_exercise(
        self,
        org_id: str,
        skill_id: str,
        title: str,
        description: str,
        exercise_type: str,
        config: dict,
        max_score: int,
        created_by: str,
    ) -> Exercise:
        try:
            etype = ExerciseType(exercise_type)
        except ValueError as exc:
            raise AppError("INVALID_EXERCISE_TYPE", f"Invalid type: {exercise_type}", 422) from exc

        exercise = Exercise(
            org_id=org_id,
            skill_id=skill_id,
            title=title,
            description=description,
            type=etype,
            config=config,
            max_score=max_score,
            created_by=created_by,
        )
        self.db.add(exercise)
        await self.db.flush()
        return exercise

    async def list_exercises(self, skill_id: str) -> list[Exercise]:
        result = await self.db.execute(
            select(Exercise)
            .where(Exercise.skill_id == skill_id, Exercise.status != ContentStatus.ARCHIVED)
            .order_by(Exercise.sort_order, Exercise.created_at)
        )
        return list(result.scalars().all())

    async def get_exercise(self, exercise_id: str) -> Exercise:
        ex = await self.db.get(Exercise, exercise_id)
        if ex is None or ex.status == ContentStatus.ARCHIVED:
            raise ExerciseNotFoundError()
        return ex

    async def get_attempt(self, attempt_id: str) -> ExerciseAttempt:
        attempt = await self.db.get(ExerciseAttempt, attempt_id)
        if attempt is None:
            raise AppError("ATTEMPT_NOT_FOUND", "Attempt not found", 404)
        return attempt

    async def update_exercise(self, exercise_id: str, **fields) -> Exercise:
        ex = await self.get_exercise(exercise_id)
        # Replacing an MCQ's config with one lacking a non-empty `correct`
        # would make every blank answer auto-grade as full marks.
        new_config = fields.get("config")
        if (
            new_config is not None
            and ex.type == ExerciseType.MULTIPLE_CHOICE
            and not new_config.get("correct")
        ):
            raise AppError(
                "INVALID_CONFIG",
                "multiple_choice config must include a non-empty 'correct'",
                422,
            )
        for k, v in fields.items():
            if v is not None and hasattr(ex, k):
                setattr(ex, k, v)
        await self.db.flush()
        return ex

    async def delete_exercise(self, exercise_id: str) -> None:
        ex = await self.get_exercise(exercise_id)
        ex.status = ContentStatus.ARCHIVED
        await self.db.flush()

    # ── Attempts ──

    async def submit_attempt(
        self,
        org_id: str,
        exercise_id: str,
        user_id: str,
        answer: dict,
    ) -> ExerciseAttempt:
        exercise = await self.get_exercise(exercise_id)

        # Check skill is unlocked
        if not await self.is_skill_unlocked(exercise.skill_id, user_id):
            raise SkillLockedError()

        attempt = ExerciseAttempt(
            org_id=org_id,
            exercise_id=exercise_id,
            user_id=user_id,
            answer=answer,
        )

        # Auto-grade MCQ. config.correct and answer.selected are untrusted:
        # coerce both to lists of strings so a malformed value can't 500 the
        # grader (sorted() on an int / mixed types raises TypeError).
        if exercise.type == ExerciseType.MULTIPLE_CHOICE:
            raw_correct = exercise.config.get("correct", [])
            if isinstance(raw_correct, (str, int, float)):
                raw_correct = [raw_correct]
            elif not isinstance(raw_correct, list):
                raw_correct = []
            correct = sorted(str(x) for x in raw_correct)

            user_answer = answer.get("selected")
            if isinstance(user_answer, (str, int, float)):
                user_answer = [user_answer]
            elif not isinstance(user_answer, list):
                user_answer = []
            user_answer = sorted(str(x) for x in user_answer)

            is_correct = user_answer == correct
            attempt.score = exercise.max_score if is_correct else 0
            attempt.is_correct = is_correct
            attempt.graded_by = GradingMethod.AUTO
            attempt.graded_at = datetime.now(UTC)
            explanation = exercise.config.get("explanation", "")
            if is_correct:
                attempt.feedback = explanation or "Correct!"
            else:
                attempt.feedback = (
                    f"Incorrect. {explanation}" if explanation else "Incorrect. Try again."
                )

        self.db.add(attempt)
        await self.db.flush()

        # Update progress
        await self._update_skill_progress(exercise.skill_id, user_id, org_id)

        return attempt

    async def get_user_attempts(self, exercise_id: str, user_id: str) -> list[ExerciseAttempt]:
        result = await self.db.execute(
            select(ExerciseAttempt)
            .where(ExerciseAttempt.exercise_id == exercise_id, ExerciseAttempt.user_id == user_id)
            .order_by(ExerciseAttempt.created_at.desc())
        )
        return list(result.scalars().all())

    async def grade_attempt(
        self,
        attempt_id: str,
        score: int,
        feedback: str | None,
    ) -> ExerciseAttempt:
        attempt = await self.db.get(ExerciseAttempt, attempt_id)
        if attempt is None:
            raise AttemptNotFoundError()

        exercise = await self.get_exercise(attempt.exercise_id)
        attempt.score = min(score, exercise.max_score)
        attempt.is_correct = score >= exercise.max_score * 0.6
        attempt.feedback = feedback
        attempt.graded_by = GradingMethod.MANUAL
        attempt.graded_at = datetime.now(UTC)
        await self.db.flush()

        await self._update_skill_progress(exercise.skill_id, attempt.user_id, attempt.org_id)
        return attempt

    async def get_pending_grading(self, org_id: str) -> list[ExerciseAttempt]:
        result = await self.db.execute(
            select(ExerciseAttempt)
            .where(
                ExerciseAttempt.org_id == org_id,
                ExerciseAttempt.graded_by.is_(None),
            )
            .order_by(ExerciseAttempt.created_at)
        )
        return list(result.scalars().all())

    # ── Progress ──

    async def is_skill_unlocked(self, skill_id: str, user_id: str) -> bool:
        prerequisites = await self.get_skill_prerequisites(skill_id)
        # An archived prerequisite can never be completed (its exercises 404),
        # so counting it would lock the dependent skill forever.
        prerequisites = [p for p in prerequisites if p.status != ContentStatus.ARCHIVED]
        if not prerequisites:
            return True

        for prereq in prerequisites:
            result = await self.db.execute(
                select(SkillProgress).where(
                    SkillProgress.skill_id == prereq.id,
                    SkillProgress.user_id == user_id,
                    SkillProgress.status == ProgressStatus.COMPLETED,
                )
            )
            if result.scalar_one_or_none() is None:
                return False
        return True

    async def get_user_progress(self, user_id: str, org_id: str) -> dict:
        # Count skills in org
        skills_result = await self.db.execute(
            select(func.count(Skill.id)).where(
                Skill.org_id == org_id,
                Skill.status != ContentStatus.ARCHIVED,
            )
        )
        skills_total = skills_result.scalar_one()

        # Count progress entries
        progress_result = await self.db.execute(
            select(SkillProgress.status, func.count(SkillProgress.id))
            .where(SkillProgress.user_id == user_id, SkillProgress.org_id == org_id)
            .group_by(SkillProgress.status)
        )
        status_counts = {row[0].value: row[1] for row in progress_result.all()}

        completed = status_counts.get("completed", 0)
        in_progress = status_counts.get("in_progress", 0)

        # Count exercises (exclude archived)
        exercises_result = await self.db.execute(
            select(func.count(Exercise.id)).where(
                Exercise.org_id == org_id,
                Exercise.status != ContentStatus.ARCHIVED,
            )
        )
        exercises_total = exercises_result.scalar_one()

        # Count completed exercises (at least one correct attempt)
        done_result = await self.db.execute(
            select(func.sum(SkillProgress.exercises_done)).where(
                SkillProgress.user_id == user_id, SkillProgress.org_id == org_id
            )
        )
        exercises_done = done_result.scalar_one() or 0

        pct = round((completed / skills_total * 100) if skills_total > 0 else 0, 1)

        # Per-category breakdown: total skills and this user's completed skills
        # per category. Was always [] — the API declared the field but never
        # populated it, so the progress UI's category view had no data.
        cat_rows = await self.db.execute(
            select(SkillCategory.id, SkillCategory.name)
            .where(
                SkillCategory.org_id == org_id,
                SkillCategory.status != ContentStatus.ARCHIVED,
            )
            .order_by(SkillCategory.sort_order, SkillCategory.name)
        )
        categories = []
        for cat_id, cat_name in cat_rows.all():
            total_r = await self.db.execute(
                select(func.count(Skill.id)).where(
                    Skill.category_id == cat_id,
                    Skill.status != ContentStatus.ARCHIVED,
                )
            )
            cat_total = total_r.scalar_one()
            done_r = await self.db.execute(
                select(func.count(SkillProgress.id))
                .join(Skill, Skill.id == SkillProgress.skill_id)
                .where(
                    Skill.category_id == cat_id,
                    Skill.status != ContentStatus.ARCHIVED,
                    SkillProgress.user_id == user_id,
                    SkillProgress.status == ProgressStatus.COMPLETED,
                )
            )
            cat_done = done_r.scalar_one()
            categories.append(
                {
                    "id": cat_id,
                    "name": cat_name,
                    "skills_total": cat_total,
                    "skills_completed": cat_done,
                    "completion_percentage": round(
                        (cat_done / cat_total * 100) if cat_total > 0 else 0, 1
                    ),
                }
            )

        return {
            "skills_total": skills_total,
            "skills_completed": completed,
            "skills_in_progress": in_progress,
            "exercises_total": exercises_total,
            "exercises_completed": exercises_done,
            "completion_percentage": pct,
            "categories": categories,
        }

    async def get_skill_progress(self, skill_id: str, user_id: str) -> SkillProgress | None:
        result = await self.db.execute(
            select(SkillProgress).where(
                SkillProgress.skill_id == skill_id, SkillProgress.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    # ── Helpers ──

    async def _set_prerequisites(self, skill_id: str, prerequisite_ids: list[str]) -> None:
        # Every prerequisite must exist AND live in the same org as the skill
        # (otherwise bogus IDs 500 on the FK and cross-org links leak data).
        if prerequisite_ids:
            skill = await self.get_skill(skill_id)
            found = await self.db.execute(
                select(Skill.id).where(Skill.id.in_(prerequisite_ids), Skill.org_id == skill.org_id)
            )
            valid = {row for row in found.scalars()}
            missing = set(prerequisite_ids) - valid
            if missing:
                raise SkillNotFoundError()

        # De-duplicate while preserving order — a repeated id would otherwise
        # violate the (skill_id, prerequisite_id) primary key with a 500.
        seen: set[str] = set()
        unique_ids = [pid for pid in prerequisite_ids if not (pid in seen or seen.add(pid))]

        # Cycle detection via BFS
        await self._detect_cycle(skill_id, unique_ids)

        # Remove existing prerequisites
        existing = await self.db.execute(
            select(SkillPrerequisite).where(SkillPrerequisite.skill_id == skill_id)
        )
        for p in existing.scalars():
            await self.db.delete(p)
        # Flush the deletes before re-inserting so a replaced-with-same set
        # doesn't collide on the primary key within one transaction.
        await self.db.flush()

        # Add new
        for pid in unique_ids:
            self.db.add(SkillPrerequisite(skill_id=skill_id, prerequisite_id=pid))
        await self.db.flush()

    async def _detect_cycle(self, skill_id: str, new_prerequisite_ids: list[str]) -> None:
        """BFS to detect if adding these prerequisites would create a cycle."""
        # Check: can we reach skill_id from any of the new prerequisites?
        visited = set()
        queue = deque(new_prerequisite_ids)

        while queue:
            current = queue.popleft()
            if current == skill_id:
                raise CyclicDependencyError()
            if current in visited:
                continue  # pragma: no cover
            visited.add(current)

            # Get prerequisites of current
            result = await self.db.execute(
                select(SkillPrerequisite.prerequisite_id).where(
                    SkillPrerequisite.skill_id == current
                )
            )
            for row in result.scalars():
                queue.append(row)

    async def _update_skill_progress(self, skill_id: str, user_id: str, org_id: str) -> None:
        exercises = await self.list_exercises(skill_id)
        total = len(exercises)

        # An exercise counts as "done" only when the learner has PASSED it —
        # a graded attempt with is_correct=True. A wrong MCQ (score=0,
        # is_correct=False) is graded but not passed; counting it as done
        # marked skills 100% complete on wrong answers and unlocked the next
        # skill. A pass threshold of 60% of max_score defines "correct" for
        # manually-graded exercises (see grade_attempt).
        done = 0
        best_score: int | None = None
        for ex in exercises:
            result = await self.db.execute(
                select(ExerciseAttempt).where(
                    ExerciseAttempt.exercise_id == ex.id,
                    ExerciseAttempt.user_id == user_id,
                )
            )
            attempts = list(result.scalars())
            if any(a.is_correct for a in attempts):
                done += 1
            # Best score = sum over exercises of the user's best graded attempt.
            # (best_score was declared + returned by the API but never written.)
            ex_scores = [a.score for a in attempts if a.score is not None]
            if ex_scores:
                best_score = (best_score or 0) + max(ex_scores)

        # Upsert progress
        result = await self.db.execute(
            select(SkillProgress).where(
                SkillProgress.skill_id == skill_id, SkillProgress.user_id == user_id
            )
        )
        progress = result.scalar_one_or_none()

        if progress is None:
            progress = SkillProgress(
                org_id=org_id,
                skill_id=skill_id,
                user_id=user_id,
            )
            self.db.add(progress)

        progress.exercises_total = total
        progress.exercises_done = done
        progress.best_score = best_score

        if done == 0:
            progress.status = ProgressStatus.NOT_STARTED
        elif done >= total and total > 0:
            progress.status = ProgressStatus.COMPLETED
            if progress.completed_at is None:
                progress.completed_at = datetime.now(UTC)
        else:
            progress.status = ProgressStatus.IN_PROGRESS
            if progress.started_at is None:
                progress.started_at = datetime.now(UTC)

        await self.db.flush()
        await self._sync_skill_badge(skill_id, user_id, org_id, progress)

    async def _sync_skill_badge(
        self, skill_id: str, user_id: str, org_id: str, progress: SkillProgress
    ) -> None:
        """Keep the portfolio SkillBadge in step with progress (ADR-007:
        badges appear automatically as skills are worked on/completed).
        Without this sync no badge row was ever created — the whole badge
        feature returned empty lists."""
        from app.models.portfolio import SkillBadge

        skill = await self.db.get(Skill, skill_id)
        if skill is None:  # pragma: no cover
            return
        category = await self.db.get(SkillCategory, skill.category_id)

        pct = 0
        if progress.exercises_total:
            pct = int(progress.exercises_done * 100 / progress.exercises_total)

        result = await self.db.execute(
            select(SkillBadge).where(
                SkillBadge.user_id == user_id,
                SkillBadge.skill_id == skill_id,
                SkillBadge.org_id == org_id,
            )
        )
        badge = result.scalar_one_or_none()
        if badge is None:
            badge = SkillBadge(
                user_id=user_id,
                skill_id=skill_id,
                org_id=org_id,
                skill_name=skill.name,
                category_name=category.name if category else "",
                completion_pct=pct,
            )
            self.db.add(badge)
        else:
            badge.skill_name = skill.name
            badge.category_name = category.name if category else ""
            badge.completion_pct = pct
        badge.completed_at = progress.completed_at
        await self.db.flush()

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:200]
