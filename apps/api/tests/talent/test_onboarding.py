"""Onboarding workflow tests — pure logic, no DB needed."""

from datetime import UTC, datetime, timedelta

from app.talent.services.onboarding import (
    ONBOARDING_PHASES,
    ONBOARDING_TASK_TYPES,
    TASK_STATUSES,
    OnboardingService,
    OnboardingTask,
    OnboardingTemplate,
)

svc = OnboardingService()


class TestConstants:
    def test_task_types(self):
        assert "document_upload" in ONBOARDING_TASK_TYPES
        assert "mentor_introduction" in ONBOARDING_TASK_TYPES
        assert len(ONBOARDING_TASK_TYPES) >= 10

    def test_statuses(self):
        assert "pending" in TASK_STATUSES
        assert "completed" in TASK_STATUSES

    def test_phases(self):
        assert ONBOARDING_PHASES[0] == "pre_start"
        assert ONBOARDING_PHASES[-1] == "first_quarter"


class TestCreateTemplate:
    def test_creates_template(self):
        t = svc.create_template(
            name="Standard", org_id="org1",
            tasks=[
                {"task_type": "document_upload", "title": "ID", "phase": "pre_start"},
                {"task_type": "team_meeting", "title": "Meet team", "phase": "day_one"},
            ],
        )
        assert t.name == "Standard"
        assert len(t.tasks) == 2

    def test_filters_invalid_task_types(self):
        t = svc.create_template(
            name="T", org_id="o",
            tasks=[{"task_type": "invalid_type", "title": "X", "phase": "day_one"}],
        )
        assert len(t.tasks) == 0

    def test_defaults_phase(self):
        t = svc.create_template(
            name="T", org_id="o",
            tasks=[{"task_type": "custom", "title": "X", "phase": "invalid"}],
        )
        assert t.tasks[0]["phase"] == "first_week"


class TestGenerateChecklist:
    def test_generates_tasks(self):
        template = OnboardingTemplate(
            name="T", org_id="o", phases=list(ONBOARDING_PHASES),
            tasks=[
                {"task_type": "document_upload", "title": "Upload ID", "description": "Scan your ID", "assigned_to": "candidate", "phase": "pre_start", "required": True},
                {"task_type": "system_access", "title": "Setup email", "description": "", "assigned_to": "employer", "phase": "day_one", "required": True},
            ],
        )
        tasks = svc.generate_checklist(template, "p1", datetime.now(UTC))
        assert len(tasks) == 2
        assert all(t.status == "pending" for t in tasks)
        assert tasks[0].assigned_to == "candidate"


class TestComputeProgress:
    def test_empty(self):
        p = svc.compute_progress([], "p1", None)
        assert p.completion_percentage == 0.0

    def test_partial(self):
        tasks = [
            OnboardingTask("custom", "A", "", "candidate", "day_one", True, None, "completed", datetime.now(UTC)),
            OnboardingTask("custom", "B", "", "candidate", "day_one", True, None, "pending", None),
            OnboardingTask("custom", "C", "", "employer", "first_week", True, None, "pending", None),
        ]
        p = svc.compute_progress(tasks, "p1", datetime.now(UTC))
        assert p.completion_percentage == round(1 / 3 * 100, 1)
        assert p.completed_tasks == 1

    def test_overdue_detection(self):
        start = datetime.now(UTC) - timedelta(days=10)
        tasks = [
            OnboardingTask("custom", "A", "", "candidate", "pre_start", True, 3, "pending", None),
        ]
        p = svc.compute_progress(tasks, "p1", start)
        assert p.overdue_tasks == 1

    def test_current_phase(self):
        tasks = [
            OnboardingTask("custom", "A", "", "candidate", "pre_start", True, None, "completed", datetime.now(UTC)),
            OnboardingTask("custom", "B", "", "candidate", "day_one", True, None, "pending", None),
        ]
        p = svc.compute_progress(tasks, "p1", datetime.now(UTC))
        assert p.current_phase == "day_one"
