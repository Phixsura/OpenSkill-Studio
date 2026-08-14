"""Skill, exercise, attempt, and progress service."""

import re
import secrets
from collections import deque
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
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
        await self.db.flush()
        return cat

    async def list_categories(self, org_id: str) -> list[SkillCategory]:
        result = await self.db.execute(
            select(SkillCategory)
            .where(SkillCategory.org_id == org_id)
            .order_by(SkillCategory.sort_order, SkillCategory.name)
        )
        return list(result.scalars().all())

    async def get_category(self, category_id: str) -> SkillCategory:
        cat = await self.db.get(SkillCategory, category_id)
        if cat is None:
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
    ) -> tuple[list[Skill], int]:
        base = select(Skill).where(Skill.org_id == org_id)

        if category_id:
            base = base.where(Skill.category_id == category_id)
        if difficulty:
            base = base.where(Skill.difficulty == DifficultyLevel(difficulty))
        if status:
            base = base.where(Skill.status == ContentStatus(status))
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
        for k, v in fields.items():
            if v is not None and hasattr(skill, k):
                if k == "difficulty":
                    v = DifficultyLevel(v)
                setattr(skill, k, v)
        await self.db.flush()
        return skill

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
            .where(Exercise.skill_id == skill_id)
            .order_by(Exercise.sort_order, Exercise.created_at)
        )
        return list(result.scalars().all())

    async def get_exercise(self, exercise_id: str) -> Exercise:
        ex = await self.db.get(Exercise, exercise_id)
        if ex is None:
            raise ExerciseNotFoundError()
        return ex

    async def update_exercise(self, exercise_id: str, **fields) -> Exercise:
        ex = await self.get_exercise(exercise_id)
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

        # Auto-grade MCQ
        if exercise.type == ExerciseType.MULTIPLE_CHOICE:
            correct = exercise.config.get("correct", [])
            user_answer = answer.get("selected", [])
            if isinstance(user_answer, str):
                user_answer = [user_answer]
            is_correct = sorted(user_answer) == sorted(correct)
            attempt.score = exercise.max_score if is_correct else 0
            attempt.is_correct = is_correct
            attempt.graded_by = GradingMethod.AUTO
            attempt.graded_at = datetime.now(UTC)
            attempt.feedback = (
                exercise.config.get("explanation", "")
                if is_correct
                else f"Incorrect. The correct answer is: {', '.join(correct)}"
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

        # Count exercises
        exercises_result = await self.db.execute(
            select(func.count(Exercise.id)).where(Exercise.org_id == org_id)
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

        return {
            "skills_total": skills_total,
            "skills_completed": completed,
            "skills_in_progress": in_progress,
            "exercises_total": exercises_total,
            "exercises_completed": exercises_done,
            "completion_percentage": pct,
            "categories": [],
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
        # Cycle detection via BFS
        await self._detect_cycle(skill_id, prerequisite_ids)

        # Remove existing prerequisites
        existing = await self.db.execute(
            select(SkillPrerequisite).where(SkillPrerequisite.skill_id == skill_id)
        )
        for p in existing.scalars():
            await self.db.delete(p)

        # Add new
        for pid in prerequisite_ids:
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

        # Count exercises with at least one correct/graded attempt
        done = 0
        for ex in exercises:
            result = await self.db.execute(
                select(ExerciseAttempt)
                .where(
                    ExerciseAttempt.exercise_id == ex.id,
                    ExerciseAttempt.user_id == user_id,
                    ExerciseAttempt.is_correct == True,  # noqa: E712
                )
                .limit(1)
            )
            if result.scalar_one_or_none():
                done += 1

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

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:200]
