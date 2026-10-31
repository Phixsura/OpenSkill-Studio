"""API Consumer Onboarding Wizard — guided multi-step onboarding wizard."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class WizardStep:
    step_id: str
    title: str
    instruction: str
    order: int
    completed: bool = False
    skippable: bool = False
    completed_at: float = 0.0

@dataclass
class OnboardingWizard:
    wizard_id: str
    consumer_id: str
    steps: list[WizardStep] = field(default_factory=list)
    current_step: int = 0
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0.0

    @property
    def progress_pct(self) -> float:
        if not self.steps: return 0.0
        done = sum(1 for s in self.steps if s.completed)
        return round((done / len(self.steps)) * 100, 1)

    @property
    def is_complete(self) -> bool:
        required = [s for s in self.steps if not s.skippable]
        return bool(required) and all(s.completed for s in required)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiOnboardingWizard:
    def __init__(self) -> None:
        self._wizards: dict[tuple[str, str], OnboardingWizard] = {}

    def create_wizard(self, installation_id: str, wizard: OnboardingWizard) -> OnboardingWizard:
        if not installation_id: raise ValueError("installation_id is required")
        if not wizard.steps: raise ValueError("Wizard must have steps")
        wizard.steps.sort(key=lambda s: s.order)
        key = (installation_id, wizard.consumer_id)
        if key in self._wizards: raise ValueError(f"Wizard for {wizard.consumer_id} exists")
        self._wizards[key] = wizard
        return wizard

    def complete_step(self, installation_id: str, consumer_id: str, step_id: str) -> OnboardingWizard:
        w = self._get(installation_id, consumer_id)
        for s in w.steps:
            if s.step_id == step_id:
                s.completed = True
                s.completed_at = time.time()
                if w.is_complete: w.completed_at = time.time()
                # Advance current step
                for i, st in enumerate(w.steps):
                    if not st.completed: w.current_step = i; break
                else: w.current_step = len(w.steps)
                return w
        raise KeyError(f"Step {step_id} not found")

    def get_wizard(self, installation_id: str, consumer_id: str) -> OnboardingWizard:
        return self._get(installation_id, consumer_id)

    def incomplete_wizards(self, installation_id: str) -> list[OnboardingWizard]:
        return [w for (inst, _), w in self._wizards.items() if inst == installation_id and not w.is_complete]

    def _get(self, installation_id: str, consumer_id: str) -> OnboardingWizard:
        w = self._wizards.get((installation_id, consumer_id))
        if w is None: raise KeyError(f"Wizard for {consumer_id} not found")
        return w
