"""App Onboarding Checklist — guide developers through app setup and publishing.

Tracks progress through required and optional onboarding steps:
- Step completion tracking with ordering
- Required vs optional steps
- Progress percentage
- Completion gating (all required steps must pass before publishing)
- Per-app checklist state
- Reset support
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class StepStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass
class ChecklistStep:
    """A single onboarding step."""

    step_id: str
    title: str
    description: str
    order: int
    required: bool = True
    status: StepStatus = StepStatus.PENDING
    completed_at: datetime | None = None


@dataclass
class ChecklistProgress:
    """Progress summary for an app's checklist."""

    app_id: str
    total_steps: int
    completed: int
    skipped: int
    pending: int
    required_completed: int
    required_total: int
    progress_pct: float
    can_publish: bool


# ── Default steps ────────────────────────────────────────

DEFAULT_STEPS = [
    ("manifest", "Complete App Manifest", "Fill in name, description, icon, and category", 1, True),
    ("permissions", "Declare Permissions", "Specify which API scopes your app needs", 2, True),
    ("oauth", "Configure OAuth", "Set redirect URIs and generate client credentials", 3, True),
    ("webhook", "Set Up Webhooks", "Configure your webhook endpoint URL and secret", 4, False),
    ("config_schema", "Define Config Schema", "Declare configurable fields for installations", 5, False),
    ("sandbox_test", "Test in Sandbox", "Run your app in the sandbox environment", 6, True),
    ("screenshots", "Add Screenshots", "Upload at least one screenshot for the marketplace", 7, True),
    ("privacy_policy", "Add Privacy Policy", "Link to your app's privacy policy URL", 8, True),
    ("review_submit", "Submit for Review", "Submit your app for marketplace review", 9, True),
]


class AppOnboardingChecklist:
    """Track developer onboarding progress per app."""

    def __init__(self):
        # app_id → list of ChecklistStep
        self._checklists: dict[str, list[ChecklistStep]] = {}

    def initialize(self, app_id: str) -> list[ChecklistStep]:
        """Create a checklist for a new app from default steps."""
        steps = [
            ChecklistStep(step_id=sid, title=title, description=desc, order=order, required=req)
            for sid, title, desc, order, req in DEFAULT_STEPS
        ]
        self._checklists[app_id] = steps
        return steps

    def get_steps(self, app_id: str) -> list[ChecklistStep]:
        return sorted(self._checklists.get(app_id, []), key=lambda s: s.order)

    def complete_step(self, app_id: str, step_id: str) -> ChecklistStep | None:
        """Mark a step as completed."""
        steps = self._checklists.get(app_id, [])
        for step in steps:
            if step.step_id == step_id:
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.now(UTC)
                return step
        return None

    def skip_step(self, app_id: str, step_id: str) -> ChecklistStep | None:
        """Skip an optional step. Required steps cannot be skipped."""
        steps = self._checklists.get(app_id, [])
        for step in steps:
            if step.step_id == step_id:
                if step.required:
                    return None  # can't skip required
                step.status = StepStatus.SKIPPED
                return step
        return None

    def reset_step(self, app_id: str, step_id: str) -> ChecklistStep | None:
        """Reset a step back to pending."""
        steps = self._checklists.get(app_id, [])
        for step in steps:
            if step.step_id == step_id:
                step.status = StepStatus.PENDING
                step.completed_at = None
                return step
        return None

    def get_progress(self, app_id: str) -> ChecklistProgress:
        """Compute overall progress."""
        steps = self._checklists.get(app_id, [])
        total = len(steps)
        completed = sum(1 for s in steps if s.status == StepStatus.COMPLETED)
        skipped = sum(1 for s in steps if s.status == StepStatus.SKIPPED)
        pending = sum(1 for s in steps if s.status == StepStatus.PENDING)
        required = [s for s in steps if s.required]
        req_completed = sum(1 for s in required if s.status == StepStatus.COMPLETED)
        req_total = len(required)
        pct = ((completed + skipped) / total * 100) if total > 0 else 0.0

        return ChecklistProgress(
            app_id=app_id,
            total_steps=total,
            completed=completed,
            skipped=skipped,
            pending=pending,
            required_completed=req_completed,
            required_total=req_total,
            progress_pct=round(pct, 1),
            can_publish=req_completed == req_total,
        )

    def get_next_step(self, app_id: str) -> ChecklistStep | None:
        """Get the next pending step in order."""
        for step in self.get_steps(app_id):
            if step.status == StepStatus.PENDING:
                return step
        return None
