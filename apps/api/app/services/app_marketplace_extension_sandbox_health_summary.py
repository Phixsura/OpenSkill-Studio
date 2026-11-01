"""Sandbox Health Summary — aggregate all sandbox health signals."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class HealthSignal:
    name: str
    healthy: bool
    message: str = ""

class SandboxHealthSummaryService:
    def __init__(self):
        self._signals: dict[str, list[HealthSignal]] = {}

    def report(self, sandbox_id: str, name: str, healthy: bool, message: str = "") -> HealthSignal:
        signal = HealthSignal(name=name, healthy=healthy, message=message)
        self._signals.setdefault(sandbox_id, [])
        # Update or add
        for i, s in enumerate(self._signals[sandbox_id]):
            if s.name == name:
                self._signals[sandbox_id][i] = signal
                return signal
        self._signals[sandbox_id].append(signal)
        return signal

    def is_healthy(self, sandbox_id: str) -> bool:
        return all(s.healthy for s in self._signals.get(sandbox_id, []))

    def get_score(self, sandbox_id: str) -> float:
        signals = self._signals.get(sandbox_id, [])
        if not signals: return 100.0
        return round(sum(1 for s in signals if s.healthy) / len(signals) * 100, 1)

    def get_issues(self, sandbox_id: str) -> list[HealthSignal]:
        return [s for s in self._signals.get(sandbox_id, []) if not s.healthy]

    def get_all(self, sandbox_id: str) -> list[HealthSignal]:
        return list(self._signals.get(sandbox_id, []))
