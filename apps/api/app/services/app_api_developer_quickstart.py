"""App API Developer Quickstart — interactive quickstart wizard."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class QuickstartStep:
    step_id: str
    title: str
    code_snippet: str = ""
    completed: bool = False

@dataclass
class QuickstartProgress:
    developer_id: str
    language: str
    steps: list[QuickstartStep] = field(default_factory=list)

    @property
    def completion_pct(self) -> float:
        if not self.steps: return 0.0
        done = sum(1 for s in self.steps if s.completed)
        return round(done / len(self.steps) * 100, 1)

class AppAPIDeveloperQuickstart:
    def __init__(self) -> None:
        self._wizards: dict[tuple[str, str], QuickstartProgress] = {}

    def start(self, installation_id: str, developer_id: str, language: str, steps: list[dict]) -> QuickstartProgress:
        if not installation_id: raise ValueError("installation_id is required")
        if not steps: raise ValueError("at least one step required")
        step_objs = [QuickstartStep(step_id=s["step_id"], title=s["title"], code_snippet=s.get("code", "")) for s in steps]
        p = QuickstartProgress(developer_id=developer_id, language=language, steps=step_objs)
        self._wizards[(installation_id, developer_id)] = p
        return p

    def complete_step(self, installation_id: str, developer_id: str, step_id: str) -> QuickstartProgress:
        p = self._get(installation_id, developer_id)
        for s in p.steps:
            if s.step_id == step_id:
                s.completed = True
                return p
        raise KeyError(f"Step {step_id} not found")

    def get_progress(self, installation_id: str, developer_id: str) -> QuickstartProgress:
        return self._get(installation_id, developer_id)

    def _get(self, installation_id: str, developer_id: str) -> QuickstartProgress:
        p = self._wizards.get((installation_id, developer_id))
        if p is None: raise KeyError(f"No quickstart for {developer_id}")
        return p
