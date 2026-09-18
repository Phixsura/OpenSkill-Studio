"""Onboarding workflow — post-hire onboarding checklist and task tracking.

Features:
  - Onboarding templates per org
  - Task assignment (candidate + employer tasks)
  - Progress tracking with completion %
  - Milestone-based progression
  - Auto-notify on task completion
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

ONBOARDING_TASK_TYPES = frozenset(
    {
        "document_upload",
        "form_completion",
        "training_module",
        "meeting_scheduled",
        "system_access",
        "equipment_setup",
        "policy_acknowledgment",
        "mentor_introduction",
        "team_meeting",
        "first_project_assignment",
        "custom",
    }
)

TASK_STATUSES = frozenset({"pending", "in_progress", "completed", "skipped", "blocked"})

ONBOARDING_PHASES = ("pre_start", "day_one", "first_week", "first_month", "first_quarter")


@dataclass(frozen=True, slots=True)
class OnboardingTask:
    task_type: str
    title: str
    description: str
    assigned_to: str  # "candidate" or "employer"
    phase: str
    required: bool
    due_days_from_start: int | None
    status: str
    completed_at: datetime | None


@dataclass(frozen=True, slots=True)
class OnboardingProgress:
    placement_id: str
    total_tasks: int
    completed_tasks: int
    completion_percentage: float
    current_phase: str
    tasks_by_phase: dict[str, dict]  # phase → {total, completed}
    overdue_tasks: int
    days_since_start: int | None


@dataclass(frozen=True, slots=True)
class OnboardingTemplate:
    name: str
    org_id: str
    tasks: list[dict]
    phases: list[str]


class OnboardingService:
    def create_template(
        self,
        *,
        name: str,
        org_id: str,
        tasks: list[dict],
    ) -> OnboardingTemplate:
        """Create a reusable onboarding template."""
        validated = []
        for t in tasks:
            if t.get("task_type") not in ONBOARDING_TASK_TYPES:
                continue
            if t.get("phase") not in ONBOARDING_PHASES:
                t["phase"] = "first_week"
            validated.append(t)
        return OnboardingTemplate(
            name=name,
            org_id=org_id,
            tasks=validated,
            phases=list(ONBOARDING_PHASES),
        )

    def generate_checklist(
        self,
        template: OnboardingTemplate,
        placement_id: str,
        start_date: datetime,
    ) -> list[OnboardingTask]:
        """Generate a concrete checklist from a template for a placement."""
        tasks = []
        for t in template.tasks:
            tasks.append(
                OnboardingTask(
                    task_type=t.get("task_type", "custom"),
                    title=t.get("title", "Untitled"),
                    description=t.get("description", ""),
                    assigned_to=t.get("assigned_to", "candidate"),
                    phase=t.get("phase", "first_week"),
                    required=t.get("required", True),
                    due_days_from_start=t.get("due_days_from_start"),
                    status="pending",
                    completed_at=None,
                )
            )
        return tasks

    def compute_progress(
        self,
        tasks: list[OnboardingTask],
        placement_id: str,
        start_date: datetime | None,
    ) -> OnboardingProgress:
        """Compute onboarding completion progress."""
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "completed")
        pct = round(completed / total * 100, 1) if total > 0 else 0.0

        by_phase: dict[str, dict] = {}
        for phase in ONBOARDING_PHASES:
            phase_tasks = [t for t in tasks if t.phase == phase]
            by_phase[phase] = {
                "total": len(phase_tasks),
                "completed": sum(1 for t in phase_tasks if t.status == "completed"),
            }

        # Current phase = first phase with incomplete tasks
        current = ONBOARDING_PHASES[-1]
        for phase in ONBOARDING_PHASES:
            if by_phase[phase]["completed"] < by_phase[phase]["total"]:
                current = phase
                break

        now = datetime.now(UTC)
        days = (now - start_date).days if start_date else None
        overdue = sum(
            1
            for t in tasks
            if t.status == "pending"
            and t.due_days_from_start is not None
            and days is not None
            and days > t.due_days_from_start
        )

        return OnboardingProgress(
            placement_id=placement_id,
            total_tasks=total,
            completed_tasks=completed,
            completion_percentage=pct,
            current_phase=current,
            tasks_by_phase=by_phase,
            overdue_tasks=overdue,
            days_since_start=days,
        )
