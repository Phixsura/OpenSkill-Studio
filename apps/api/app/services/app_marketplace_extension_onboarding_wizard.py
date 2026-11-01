"""Onboarding Wizard — guide developers through extension setup.

Multi-step wizard with validation per step, progress persistence,
skip/back support, and completion tracking.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field


@dataclass
class WizardStep:
    step_id: str
    title: str
    description: str
    required: bool = True
    completed: bool = False
    skipped: bool = False
    data: dict = field(default_factory=dict)


@dataclass
class WizardSession:
    session_id: str
    extension_id: str
    developer_id: str
    steps: list[WizardStep]
    current_step: int = 0
    completed: bool = False


class ExtensionOnboardingWizardService:
    """Multi-step onboarding wizard for extension developers."""

    DEFAULT_STEPS = [
        ("basics", "Extension Basics", "Name, description, category", True),
        ("manifest", "Create Manifest", "Configure manifest.json", True),
        ("permissions", "Set Permissions", "Declare required permissions", True),
        ("branding", "Add Branding", "Icon, screenshots, colors", False),
        ("testing", "Test Extension", "Run test suite", True),
        ("review", "Submit for Review", "Final review checklist", True),
    ]

    def __init__(self):
        self._sessions: dict[str, WizardSession] = {}

    def start(self, extension_id: str, developer_id: str) -> WizardSession:
        session_id = f"wiz_{secrets.token_urlsafe(8)}"
        steps = [WizardStep(step_id=sid, title=title, description=desc, required=req)
                 for sid, title, desc, req in self.DEFAULT_STEPS]
        session = WizardSession(
            session_id=session_id, extension_id=extension_id,
            developer_id=developer_id, steps=steps,
        )
        self._sessions[session_id] = session
        return session

    def complete_step(self, session_id: str, data: dict | None = None) -> dict:
        session = self._sessions.get(session_id)
        if not session or session.completed:
            return {"ok": False, "error": "Invalid session"}
        if session.current_step >= len(session.steps):
            return {"ok": False, "error": "All steps done"}

        step = session.steps[session.current_step]
        step.completed = True
        step.data = data or {}
        session.current_step += 1

        if session.current_step >= len(session.steps):
            session.completed = True
            return {"ok": True, "completed": True}

        return {"ok": True, "next": session.steps[session.current_step].title}

    def skip_step(self, session_id: str) -> dict:
        session = self._sessions.get(session_id)
        if not session:
            return {"ok": False, "error": "Invalid session"}
        step = session.steps[session.current_step]
        if step.required:
            return {"ok": False, "error": "Cannot skip required step"}
        step.skipped = True
        session.current_step += 1
        if session.current_step >= len(session.steps):
            session.completed = True
        return {"ok": True}

    def go_back(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session or session.current_step == 0:
            return False
        session.current_step -= 1
        return True

    def get_progress(self, session_id: str) -> dict:
        session = self._sessions.get(session_id)
        if not session:
            return {}
        done = sum(1 for s in session.steps if s.completed or s.skipped)
        return {
            "current_step": session.current_step,
            "total_steps": len(session.steps),
            "completed": done,
            "percent": round(done / len(session.steps) * 100),
            "is_complete": session.completed,
        }
