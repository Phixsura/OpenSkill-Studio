"""App Release Gate — enforce quality gates before releases.

Manages release quality gates for installed apps:
- Define gate checks (test pass, coverage, review approval)
- Track gate status per release
- Block or approve releases based on gate results
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class GateStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class GateCheck:
    """A quality gate check."""

    gate_id: str
    name: str
    required: bool = True
    status: GateStatus = GateStatus.PENDING
    message: str = ""


@dataclass
class ReleaseGateResult:
    """Overall gate result for a release."""

    version: str
    gates: list[GateCheck]
    approved: bool = False

    @property
    def all_required_passed(self) -> bool:
        required = [g for g in self.gates if g.required]
        return bool(required) and all(
            g.status == GateStatus.PASSED for g in required
        )

    @property
    def failed_gates(self) -> list[GateCheck]:
        return [g for g in self.gates if g.status == GateStatus.FAILED]


class AppReleaseGate:
    """Enforce quality gates before releases."""

    def __init__(self) -> None:
        # (installation_id, version) → ReleaseGateResult
        self._results: dict[tuple[str, str], ReleaseGateResult] = {}

    def create_release_gates(
        self,
        installation_id: str,
        version: str,
        gates: list[dict],
    ) -> ReleaseGateResult:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not version:
            raise ValueError("version is required")
        if not gates:
            raise ValueError("at least one gate is required")

        key = (installation_id, version)
        if key in self._results:
            raise ValueError(f"Gates for {version} already exist")

        gate_checks = [
            GateCheck(
                gate_id=g["gate_id"], name=g["name"],
                required=g.get("required", True),
            )
            for g in gates
        ]
        result = ReleaseGateResult(version=version, gates=gate_checks)
        self._results[key] = result
        return result

    def update_gate(
        self,
        installation_id: str,
        version: str,
        gate_id: str,
        status: GateStatus,
        message: str = "",
    ) -> GateCheck:
        result = self._get(installation_id, version)
        for g in result.gates:
            if g.gate_id == gate_id:
                g.status = status
                g.message = message
                # Recompute approval on any gate change
                result.approved = result.all_required_passed
                return g
        raise KeyError(f"Gate {gate_id} not found")

    def check_approval(self, installation_id: str, version: str) -> bool:
        """Check if all required gates passed → approve release."""
        result = self._get(installation_id, version)
        result.approved = result.all_required_passed
        return result.approved

    def get_result(self, installation_id: str, version: str) -> ReleaseGateResult:
        return self._get(installation_id, version)

    def list_versions(self, installation_id: str) -> list[str]:
        return [v for (inst, v) in self._results if inst == installation_id]

    def _get(self, installation_id: str, version: str) -> ReleaseGateResult:
        key = (installation_id, version)
        r = self._results.get(key)
        if r is None:
            raise KeyError(f"No gates for version {version}")
        return r
