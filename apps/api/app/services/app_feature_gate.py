"""App Feature Gate — conditional feature access based on entitlements.

Manages feature entitlements for installed apps:
- Define feature gates with conditions
- Check access by plan, role, or custom attributes
- Track gate evaluations
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class GateCondition:
    """A condition for feature access."""

    attribute: str   # "plan", "role", "country", custom key
    operator: str    # "eq", "in", "gte", "lte"
    value: object    # string, list, or number


@dataclass
class FeatureGate:
    """A feature gate with conditions."""

    gate_id: str
    name: str
    conditions: list[GateCondition]
    match_all: bool = True  # True=AND, False=OR
    eval_count: int = 0
    pass_count: int = 0


class AppFeatureGate:
    """Conditional feature access based on entitlements."""

    def __init__(self) -> None:
        self._gates: dict[tuple[str, str], FeatureGate] = {}

    def define_gate(
        self,
        installation_id: str,
        gate_id: str,
        name: str,
        conditions: list[dict],
        match_all: bool = True,
    ) -> FeatureGate:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not gate_id:
            raise ValueError("gate_id is required")
        if not conditions:
            raise ValueError("at least one condition required")

        conds = [
            GateCondition(attribute=c["attribute"], operator=c["operator"], value=c["value"])
            for c in conditions
        ]
        gate = FeatureGate(gate_id=gate_id, name=name, conditions=conds, match_all=match_all)
        self._gates[(installation_id, gate_id)] = gate
        return gate

    def evaluate(
        self, installation_id: str, gate_id: str, context: dict
    ) -> bool:
        """Evaluate a gate against a user context."""
        gate = self._get(installation_id, gate_id)
        gate.eval_count += 1

        results = [self._check_condition(c, context) for c in gate.conditions]
        passed = all(results) if gate.match_all else any(results)

        if passed:
            gate.pass_count += 1
        return passed

    def get_gate(self, installation_id: str, gate_id: str) -> FeatureGate:
        return self._get(installation_id, gate_id)

    def list_gates(self, installation_id: str) -> list[FeatureGate]:
        return [g for (inst, _), g in self._gates.items() if inst == installation_id]

    def pass_rate(self, installation_id: str, gate_id: str) -> float:
        gate = self._get(installation_id, gate_id)
        return round(gate.pass_count / gate.eval_count * 100, 1) if gate.eval_count > 0 else 0

    def _check_condition(self, cond: GateCondition, ctx: dict) -> bool:
        val = ctx.get(cond.attribute)
        if val is None:
            return False
        if cond.operator == "eq":
            return val == cond.value
        if cond.operator == "in":
            return val in cond.value if isinstance(cond.value, list) else False
        if cond.operator == "gte":
            return val >= cond.value
        if cond.operator == "lte":
            return val <= cond.value
        return False

    def _get(self, installation_id: str, gate_id: str) -> FeatureGate:
        key = (installation_id, gate_id)
        g = self._gates.get(key)
        if g is None:
            raise KeyError(f"Gate {gate_id} not found")
        return g
