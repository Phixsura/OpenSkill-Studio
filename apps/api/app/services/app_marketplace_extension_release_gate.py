"""Release Gate — enforce quality gates before extension releases.

Defines a set of required checks (tests, security, compliance, review)
that must all pass before an extension version can be released.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class GateStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class GateCheck:
    name: str
    status: GateStatus = GateStatus.PENDING
    message: str = ""
    required: bool = True
    checked_at: str = ""


@dataclass
class ReleaseGate:
    gate_id: str
    extension_id: str
    version: str
    checks: list[GateCheck]
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    @property
    def can_release(self) -> bool:
        required = [c for c in self.checks if c.required]
        return all(c.status == GateStatus.PASSED for c in required)

    @property
    def overall_status(self) -> str:
        if any(c.status == GateStatus.FAILED and c.required for c in self.checks):
            return "blocked"
        if all(c.status in (GateStatus.PASSED, GateStatus.SKIPPED) for c in self.checks):
            return "ready"
        return "pending"


DEFAULT_CHECKS = [
    "tests_pass", "security_scan", "compliance_check",
    "manifest_valid", "size_limit", "peer_review",
]


class ReleaseGateService:
    """Manages quality gates for extension releases."""

    def __init__(self):
        self._gates: dict[str, ReleaseGate] = {}

    def create_gate(self, extension_id: str, version: str,
                    checks: list[str] | None = None,
                    optional_checks: list[str] | None = None) -> ReleaseGate:
        gate_id = f"{extension_id}@{version}"
        check_names = checks or DEFAULT_CHECKS
        optional = set(optional_checks or [])
        gate_checks = [GateCheck(name=n, required=n not in optional) for n in check_names]
        gate = ReleaseGate(gate_id, extension_id, version, gate_checks)
        self._gates[gate_id] = gate
        return gate

    def update_check(self, extension_id: str, version: str, check_name: str,
                     status: GateStatus, message: str = "") -> bool:
        gate = self._gates.get(f"{extension_id}@{version}")
        if not gate:
            return False
        for check in gate.checks:
            if check.name == check_name:
                check.status = status
                check.message = message
                check.checked_at = datetime.now(timezone.utc).isoformat()
                return True
        return False

    def get_gate(self, extension_id: str, version: str) -> ReleaseGate | None:
        return self._gates.get(f"{extension_id}@{version}")

    def can_release(self, extension_id: str, version: str) -> tuple[bool, list[str]]:
        gate = self.get_gate(extension_id, version)
        if not gate:
            return False, ["No gate found"]
        if gate.can_release:
            return True, []
        blockers = [c.name for c in gate.checks if c.required and c.status != GateStatus.PASSED]
        return False, blockers

    def get_summary(self, extension_id: str, version: str) -> dict | None:
        gate = self.get_gate(extension_id, version)
        if not gate:
            return None
        return {
            "gate_id": gate.gate_id,
            "overall": gate.overall_status,
            "can_release": gate.can_release,
            "checks": [{"name": c.name, "status": c.status.value, "required": c.required,
                         "message": c.message} for c in gate.checks],
            "passed": sum(1 for c in gate.checks if c.status == GateStatus.PASSED),
            "total": len(gate.checks),
        }
