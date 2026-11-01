"""App API Developer Getting Started Wizard — step-by-step onboarding wizard."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

WIZARD_STEPS = ["create_account", "generate_api_key", "make_first_call", "configure_webhook", "go_live"]

@dataclass
class WizardProgress:
    developer_id: str
    completed_steps: list[str] = field(default_factory=list)
    current_step: str = "create_account"
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None

    @property
    def progress_pct(self) -> float:
        return round(len(self.completed_steps) / len(WIZARD_STEPS) * 100, 1)

    @property
    def is_complete(self) -> bool:
        return len(self.completed_steps) == len(WIZARD_STEPS)

    @property
    def next_step(self) -> str | None:
        for step in WIZARD_STEPS:
            if step not in self.completed_steps: return step
        return None

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizard:
    def __init__(self) -> None:
        self._progress: dict[tuple[str, str], WizardProgress] = {}

    def start(self, installation_id: str, developer_id: str) -> WizardProgress:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, developer_id)
        if key in self._progress: raise ValueError("Wizard already started")
        p = WizardProgress(developer_id=developer_id)
        self._progress[key] = p
        return p

    def complete_step(self, installation_id: str, developer_id: str, step: str) -> WizardProgress:
        if step not in WIZARD_STEPS: raise ValueError(f"Invalid step: {step}")
        p = self._get(installation_id, developer_id)
        if step not in p.completed_steps:
            p.completed_steps.append(step)
        p.current_step = p.next_step or "done"
        if p.is_complete: p.completed_at = time.time()
        return p

    def get_progress(self, installation_id: str, developer_id: str) -> WizardProgress:
        return self._get(installation_id, developer_id)

    def completion_rate(self, installation_id: str) -> float:
        progs = [p for (inst, _), p in self._progress.items() if inst == installation_id]
        if not progs: return 0.0
        return round(sum(1 for p in progs if p.is_complete) / len(progs) * 100, 1)

    def _get(self, installation_id: str, developer_id: str) -> WizardProgress:
        key = (installation_id, developer_id)
        p = self._progress.get(key)
        if p is None: raise KeyError(f"No wizard for {developer_id}")
        return p
