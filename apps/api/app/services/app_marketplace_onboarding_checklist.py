"""Onboarding Checklist — guide new developers through platform setup.

Tracks completion of required and optional onboarding steps,
provides progress metrics, and unlocks capabilities as steps complete.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ChecklistStep:
    step_id: str
    title: str
    description: str
    required: bool = True
    completed: bool = False
    completed_at: str = ""
    unlocks: list[str] = field(default_factory=list)


DEFAULT_STEPS = [
    ChecklistStep("profile", "Complete Developer Profile", "Add your name, bio, and avatar", required=True, unlocks=["create_extension"]),
    ChecklistStep("api_key", "Generate API Key", "Create your first API key for development", required=True, unlocks=["api_access"]),
    ChecklistStep("first_ext", "Create First Extension", "Initialize your first extension project", required=True, unlocks=["publish"]),
    ChecklistStep("add_tests", "Add Tests", "Write tests for your extension", required=True, unlocks=["ci_integration"]),
    ChecklistStep("security_scan", "Pass Security Scan", "Run and pass the security scanner", required=True, unlocks=["marketplace_listing"]),
    ChecklistStep("docs", "Write Documentation", "Add a README and API docs", required=False),
    ChecklistStep("webhook", "Set Up Webhooks", "Configure event notifications", required=False),
    ChecklistStep("publish", "Publish to Marketplace", "Submit your first extension", required=False, unlocks=["analytics_dashboard"]),
]


class OnboardingChecklistService:
    """Manages developer onboarding checklists."""

    def __init__(self):
        self._checklists: dict[str, list[ChecklistStep]] = {}

    def create_checklist(self, developer_id: str) -> list[ChecklistStep]:
        steps = [ChecklistStep(s.step_id, s.title, s.description, s.required, unlocks=list(s.unlocks)) for s in DEFAULT_STEPS]
        self._checklists[developer_id] = steps
        return steps

    def complete_step(self, developer_id: str, step_id: str) -> tuple[bool, list[str]]:
        """Complete a step. Returns (success, newly_unlocked_capabilities)."""
        steps = self._checklists.get(developer_id, [])
        for step in steps:
            if step.step_id == step_id and not step.completed:
                step.completed = True
                step.completed_at = datetime.now(timezone.utc).isoformat()
                return True, step.unlocks
        return False, []

    def get_progress(self, developer_id: str) -> dict:
        steps = self._checklists.get(developer_id, [])
        if not steps:
            return {"developer_id": developer_id, "exists": False}
        total = len(steps)
        completed = sum(1 for s in steps if s.completed)
        required = [s for s in steps if s.required]
        required_done = sum(1 for s in required if s.completed)
        return {
            "developer_id": developer_id,
            "total_steps": total,
            "completed": completed,
            "percent": round(completed / max(1, total) * 100, 1),
            "required_done": required_done,
            "required_total": len(required),
            "all_required_complete": required_done == len(required),
            "next_step": next((s.step_id for s in steps if not s.completed), None),
        }

    def get_unlocked_capabilities(self, developer_id: str) -> list[str]:
        steps = self._checklists.get(developer_id, [])
        caps = []
        for s in steps:
            if s.completed:
                caps.extend(s.unlocks)
        return sorted(set(caps))

    def reset(self, developer_id: str) -> bool:
        if developer_id in self._checklists:
            for step in self._checklists[developer_id]:
                step.completed = False
                step.completed_at = ""
            return True
        return False
