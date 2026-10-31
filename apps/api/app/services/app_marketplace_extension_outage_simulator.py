"""Outage Simulator — game day framework for planned failure testing.

Implements:
- Define outage scenarios with affected components
- Simulate cascading failures through dependency graph
- Track system behavior during simulated outage
- Measure recovery time (MTTR)
- Generate post-mortem reports
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class OutageScenario:
    scenario_id: str
    name: str
    description: str
    affected_components: list[str]
    expected_impact: str
    duration_seconds: float = 0
    cascading: bool = True


@dataclass
class SimulationEvent:
    timestamp: float
    component: str
    event_type: str  # failed, degraded, recovered, cascading_failure
    message: str = ""


@dataclass
class SimulationResult:
    scenario_id: str
    events: list[SimulationEvent] = field(default_factory=list)
    started_at: float = 0
    recovered_at: float = 0
    total_affected: int = 0
    mttr_seconds: float = 0  # mean time to recovery
    status: str = "pending"  # pending, running, completed


class OutageSimulatorService:
    def __init__(self):
        self._components: dict[str, list[str]] = {}  # component -> dependencies
        self._scenarios: dict[str, OutageScenario] = {}
        self._results: list[SimulationResult] = []

    def register_component(self, name: str, dependencies: list[str] | None = None) -> None:
        self._components[name] = dependencies or []

    def define_scenario(self, scenario_id: str, name: str, description: str,
                        affected: list[str], expected_impact: str = "",
                        cascading: bool = True) -> OutageScenario:
        scenario = OutageScenario(scenario_id=scenario_id, name=name,
                                  description=description,
                                  affected_components=affected,
                                  expected_impact=expected_impact,
                                  cascading=cascading)
        self._scenarios[scenario_id] = scenario
        return scenario

    def simulate(self, scenario_id: str) -> SimulationResult:
        """Run the outage simulation."""
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            raise ValueError("Scenario not found")

        result = SimulationResult(scenario_id=scenario_id, started_at=time.time())
        result.status = "running"
        failed = set()

        # Direct failures
        for comp in scenario.affected_components:
            if comp in self._components:
                result.events.append(SimulationEvent(
                    timestamp=time.time(), component=comp,
                    event_type="failed", message=f"Direct failure: {comp}"))
                failed.add(comp)

        # Cascading failures
        if scenario.cascading:
            changed = True
            rounds = 0
            while changed and rounds < 20:
                changed = False
                rounds += 1
                for comp, deps in self._components.items():
                    if comp in failed:
                        continue
                    failed_deps = [d for d in deps if d in failed]
                    if failed_deps:
                        result.events.append(SimulationEvent(
                            timestamp=time.time(), component=comp,
                            event_type="cascading_failure",
                            message=f"Cascade: {comp} failed due to {failed_deps}"))
                        failed.add(comp)
                        changed = True

        result.total_affected = len(failed)

        # Simulate recovery (reverse order)
        recovery_start = time.time()
        for comp in reversed(list(failed)):
            result.events.append(SimulationEvent(
                timestamp=time.time(), component=comp,
                event_type="recovered", message=f"Recovered: {comp}"))

        result.recovered_at = time.time()
        result.mttr_seconds = round(result.recovered_at - result.started_at, 3)
        result.status = "completed"
        self._results.append(result)
        return result

    def generate_postmortem(self, result: SimulationResult) -> dict:
        """Generate a post-mortem report from simulation results."""
        scenario = self._scenarios.get(result.scenario_id)
        direct = [e for e in result.events if e.event_type == "failed"]
        cascading = [e for e in result.events if e.event_type == "cascading_failure"]
        recovered = [e for e in result.events if e.event_type == "recovered"]

        return {
            "scenario": scenario.name if scenario else "Unknown",
            "description": scenario.description if scenario else "",
            "direct_failures": len(direct),
            "cascading_failures": len(cascading),
            "total_affected": result.total_affected,
            "total_components": len(self._components),
            "blast_radius_pct": round(result.total_affected / max(1, len(self._components)) * 100, 1),
            "mttr_seconds": result.mttr_seconds,
            "timeline": [{"component": e.component, "type": e.event_type,
                           "message": e.message} for e in result.events],
            "recommendations": self._recommendations(result, cascading),
        }

    def _recommendations(self, result: SimulationResult,
                         cascading: list[SimulationEvent]) -> list[str]:
        recs = []
        if len(cascading) > 2:
            recs.append("High cascade depth — add circuit breakers between components")
        if result.total_affected > len(self._components) * 0.5:
            recs.append("Blast radius > 50% — reduce single points of failure")
        if not cascading:
            recs.append("No cascading failures — good isolation between components")
        return recs

    def get_scenarios(self) -> list[dict]:
        return [{"id": s.scenario_id, "name": s.name,
                 "affected": s.affected_components}
                for s in self._scenarios.values()]
